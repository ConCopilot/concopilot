# -*- coding: utf-8 -*-

import json
import logging
import time

from typing import Dict, Tuple, Optional

from concopilot.framework.plugin import Plugin, PluginManager
from concopilot.framework.cerebrum import InteractParameter, InteractResponse, AbstractCerebrum
from concopilot.framework.resource.category.model import LLM
from concopilot.util import ClassDict
from concopilot.util.jsons import JsonEncoder


logger=logging.getLogger(__file__)


class OpenAICerebrum(AbstractCerebrum):
    def __init__(self, config):
        super(OpenAICerebrum, self).__init__(config)
        self._model: LLM = None
        self.max_tokens: int = self.config.config.max_tokens
        self._instruction_prompt: str = f'Make your response less than {self.max_tokens} tokens.'
        self._plugin_prompt: str = None
        self._functions=[]
        self._function_plugin_map: Dict[str, Tuple[str, str]] = {}
        self._function_failed_plugins: Dict[str, Plugin] = {}

    def setup_plugins(self, plugin_manager: PluginManager):
        self._functions=[]
        self._function_plugin_map={}
        self._function_failed_plugins={}
        if plugin_manager is not None:
            if self.config.config.use_function_call:
                for plugin in plugin_manager.plugins:
                    if not self.create_plugin_function(plugin):
                        self._function_failed_plugins[plugin.name]=plugin
                if len(self._function_failed_plugins)>0:
                    with open(self.config_file_path(self.config.config.instruction_file)) as file:
                        self._plugin_prompt=file.read().replace('{plugins}', '\n\n'.join([plugin.prompt for plugin in self._function_failed_plugins.values()]))
            else:
                with open(self.config_file_path(self.config.config.instruction_file)) as file:
                    self._plugin_prompt=file.read().replace('{plugins}', plugin_manager.get_combined_prompt())

    def instruction_prompt(self) -> Optional[str]:
        return self._instruction_prompt

    @property
    def model(self) -> LLM:
        if self._model is None:
            self._model=self.resources[0]
            assert isinstance(self._model, LLM)
        return self._model

    def interact(self, param: InteractParameter, **kwargs) -> InteractResponse:
        prompt='\n\n'.join(param.instructions)
        if self._plugin_prompt is not None and self._plugin_prompt.strip()!='':
            prompt+='\n\n'+self._plugin_prompt
        current_context = [
            OpenAICerebrum.create_chat_message('system', prompt),
            OpenAICerebrum.create_chat_message(
                'system', f"The current time and date is {time.strftime('%c')}"
            )
        ]

        if self.instruction_prompt():
            current_context.append(OpenAICerebrum.create_chat_message('system', self.instruction_prompt()))

        if param.assets is not None and len(param.assets)>0:
            current_context.append(OpenAICerebrum.create_chat_message('system', 'Below are assets for your reference:\n\n'+json.dumps(param.assets, cls=JsonEncoder, ensure_ascii=False)))

        if param.message_history is not None and len(param.message_history)>0:
            # current_context.append(OpenAICerebrum.create_chat_message('system', 'Below are the nearest interaction messages between you, plugins, and the user so far, aiming to remind you for your recent works:'))
            for msg in param.message_history:
                if msg.sender.role=='user':
                    role='user'
                elif msg.sender.role=='cerebrum':
                    role='assistant'
                elif msg.sender.role=='plugin':
                    if self.config.config.use_function_call and msg.sender.name+'_'+msg.content.command in self._function_plugin_map:
                        role='function'
                    else:
                        role='system'
                elif msg.sender.role:
                    role=msg.sender.role
                else:
                    role='system'

                function_call=None
                name=None
                if self.config.config.use_function_call and role=='assistant' and msg.receiver.role=='plugin' and msg.content is not None and msg.receiver.name+'_'+msg.content.command in self._function_plugin_map:
                    content=None
                    function_call={
                        'name': msg.receiver.name+'_'+msg.content.command,
                        'arguments': json.dumps(msg.content.param, cls=JsonEncoder, ensure_ascii=False)
                    }
                elif role=='function':
                    content=msg.content.content if isinstance(msg.content.content, str) else json.dumps(msg.content.content, cls=JsonEncoder, ensure_ascii=False)
                    name=msg.owner.name+'_'+msg.owner.command
                else:
                    content=json.dumps(msg, cls=JsonEncoder, ensure_ascii=False)

                current_context.append(OpenAICerebrum.create_chat_message(role, content, function_call, name))

        if param.content:
            current_context.append(OpenAICerebrum.create_chat_message('system', param.content))

        if param.command:
            current_context.append(OpenAICerebrum.create_chat_message('user', param.command))

        inference_param={
            'messages': current_context,
            'max_tokens': self.max_tokens,
            'require_token_len': param.require_token_len,
            'require_cost': param.require_cost
        }
        if len(self._functions)>0:
            inference_param['functions']=self._functions
            inference_param['function_call']='auto'
        reply=self.model.inference(inference_param)
        reply.plugin_call=self.get_plugin_call(reply.pop('function_call', None))

        return InteractResponse(**reply)

    @staticmethod
    def create_chat_message(role, content, function_call: Dict = None, name: str = None):
        msg={'role': role, 'content': content}
        if function_call is not None:
            msg['function_call']=function_call
        if name is not None:
            msg['name']=name
        return msg

    def create_plugin_function(self, plugin: Plugin) -> bool:
        flag=True
        for command in plugin.config.commands:
            try:
                func=ClassDict()
                func.name=plugin.name+'_'+command.command_name
                func.description=plugin.config.info.description_for_model if plugin.config.info.description_for_model else plugin.config.info.description
                func.parameters=ClassDict(
                    type='object',
                    properties=ClassDict(),
                    required=[]
                )
                for param in command.parameters:
                    func.parameters.properties[param.name]=ClassDict(type=get_function_call_data_type(param.type))
                    if param.description:
                        func.parameters.properties[param.name].description=param.description
                    if param.enum:
                        func.parameters.properties[param.name].enum=param.enum
                    if param.required:
                        func.parameters.required.append(param.name)

                self._functions.append(func)
                self._function_plugin_map[func.name]=(plugin.name, command.command_name)
            except Exception as e:
                flag=False
                logger.warning(f'Converting plugin command to function call failed. Plugin `{plugin.name}`, command `{command.command_name}`, will use prompt instead.', exc_info=e)

        return flag

    def get_plugin_call(self, function_call: Dict) -> Optional[InteractResponse.PluginCall]:
        if function_call is not None:
            plugin_name, command=self._function_plugin_map[function_call['name']]
            param=ClassDict.convert(json.loads(function_call['arguments']))
            return InteractResponse.PluginCall(
                plugin_name=plugin_name,
                command=command,
                param=param
            )
        else:
            return None


def get_function_call_data_type(type: str):
    type=type.lower()
    return TYPES[type]


TYPES={
    'integer': 'integer',
    'int': 'integer',
    'boolean': 'boolean',
    'bool': 'boolean',
    'string': 'string',
    'str': 'string'
}
