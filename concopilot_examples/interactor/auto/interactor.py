# -*- coding: utf-8 -*-

import json
import logging

from typing import Dict, List, Tuple

from concopilot.framework.plugin import PluginManager
from concopilot.framework.interactor import BasicInteractor
from concopilot.framework.resource import ResourceManager
from concopilot.framework.cerebrum import InteractParameter, InteractResponse, Cerebrum
from concopilot.framework.message import Message
from concopilot.framework.message.manager import MessageManager
from concopilot.util.context import Asset
from concopilot.util.identity import Identity
from concopilot.util.initializer import component
from concopilot.util.jsons import JsonEncoder
from concopilot.util.error import ConcopilotError
from concopilot.util import ClassDict
from concopilot import Settings


settings=Settings()
logger=logging.getLogger(__file__)


class AutoInteractor(BasicInteractor):
    def __init__(
        self,
        config: Dict,
        resource_manager: ResourceManager,
        cerebrum: Cerebrum,
        plugin_manager: PluginManager,
        message_manager: MessageManager
    ):
        super(AutoInteractor, self).__init__(
            config,
            resource_manager,
            cerebrum,
            plugin_manager,
            message_manager
        )
        with open(self.config_file_path(self.config.config.instruction_file)) as file:
            self.instruction: str = file.read()
        self.goals: List[str] = None
        self.instructions: List[str] = None
        self.message_history_key=self.config.config.message_history_key
        self.message_history_start_key=self.config.config.message_history_key+'_start'
        self.message_summary_key=self.config.config.message_summary_key
        self.summarize_token_len=self.config.config.summarize_token_len
        self.summarizer=component.create_component(self.config.config.summarizer)
        self.llm_param={}

    def config_resources(self, resource_manager: ResourceManager):
        super(AutoInteractor, self).config_resources(resource_manager)
        self.summarizer.config_resources(resource_manager)

    def interact_loop(self):
        cerebrum_command='Determine which next command to use, and respond using the json format specified above.'

        message_history: List[Message] = self.context.storage.get_or_default(self.message_history_key, [])
        message_history_start: int = self.context.storage.get_or_default(self.message_history_start_key, 0)
        msg_summary: str = self.context.storage.get_or_default(self.message_summary_key, 'No summary currently.')
        self.context.assets[self.message_summary_key]=Asset(
            type='text',
            name='message summary',
            description='The summary of interaction messages between you, plugins, and the user. This is for reminding you with events from your past.',
            content=msg_summary
        )
        while True:
            try:
                if self.context.user_interface.has_user_msg():
                    count=0
                    while msg:=self.context.user_interface.get_user_msg():
                        if msg is not None:
                            if msg.receiver and msg.receiver.role=='interactor' and msg.content:
                                self.command(command_name=msg.content.command, param=msg.content.param)
                            else:
                                AutoInteractor._check_msg(msg, Identity(role='user', id=None, name=None))
                                message_history.append(msg)
                                count+=1
                        if not self.context.user_interface.has_user_msg():
                            break
                    cerebrum_command=cerebrum_command+f' Note that {count} incoming user message detected.'

                response, message_history_start=self._interact_with_cerebrum(cerebrum_command, message_history, message_history_start, self.context.assets)
                try:
                    msg=self.message_manager.parse(response)
                except Exception as e:
                    logger.error('Failed to parse the cerebrum response message.', exc_info=e)
                    raise ConcopilotError('Failed to parse the cerebrum response message, maybe the response format is not acceptable.')
                AutoInteractor._check_msg(msg, Identity(role='cerebrum', id=self.cerebrum.id, name=self.cerebrum.name))

                message_history.append(Message(
                    sender=Identity(role='user'),
                    receiver=Identity(role='cerebrum', id=self.cerebrum.id, name=self.cerebrum.name),
                    content=Message.Content(text=cerebrum_command),
                    time=settings.current_time()
                ))
                message_history.append(msg)
                self.context.storage.put(self.message_history_key, message_history)

                cerebrum_command='Determine which next command to use, and respond using the format specified above.'
                if msg.receiver is not None:
                    if msg.receiver.role=='system':
                        if msg.content.text=='error' or msg.content.command=='error':
                            cerebrum_command='Last command execution threw an error. Check the error in the interaction messages, and try to fix the error and determine which next command to use, and respond using the json format specified above.'
                        elif msg.content.command=='exit' or msg.content.text=='exit':
                            break
                        else:
                            raise ValueError(f'Unknown "command" in the "content" section! Got "{msg.content.command}", but only "error" and "exit" are acceptable.')
                    elif msg.receiver.role=='user':
                        self.context.user_interface.send_msg_user(msg)
                        while msg:=self.context.user_interface.wait_user_msg():
                            if msg is not None:
                                if msg.receiver and msg.receiver.role=='interactor' and msg.content:
                                    self.command(command_name=msg.content.command, param=msg.content.param)
                                else:
                                    break
                            else:
                                logger.error('User interface pipeline is broken. Will exit.')
                                break
                        if not msg:
                            break
                        AutoInteractor._check_msg(msg, Identity(role='user', id=None, name=None))
                        message_history.append(msg)
                    elif msg.receiver.role=='plugin':
                        plugin=self.plugin_manager.get_plugin(name=msg.receiver.name)
                        if plugin is None:
                            raise ValueError(f'No such plugin with the name: {msg.receiver.name}.')
                        msg=plugin.on_msg(msg)
                        AutoInteractor._check_msg(msg, Identity(role='plugin', id=plugin.id, name=plugin.name))
                        message_history.append(msg)
                    else:
                        raise ValueError(f'Unknown "role" in the "receiver" section! Got "{msg.receiver.role}", but only "system", "user", and "plugin" are acceptable.')
            except Exception as e:
                logger.error('An error happened during the thinking loop.', exc_info=e)
                msg=Message(
                    sender=Identity(role='system'),
                    receiver=Identity(role='cerebrum', id=self.cerebrum.id, name=self.cerebrum.name),
                    content=Message.Content(
                        text='error',
                        data=f'{str(e.__class__.__name__)}: {str(e)}'
                    )
                )
                AutoInteractor._check_msg(msg, Identity(role='system', id=None, name=None))
                message_history.append(msg)
                cerebrum_command='An error happened during the thinking loop. Check the error in the interaction messages, and try to fix the error and determine which next command to use, and respond using the json format specified above.'

    @staticmethod
    def _check_msg(msg: Message, sender: Identity) -> Message:
        if sender is not None:
            msg.sender=sender
        msg.time=settings.current_time()
        logger.info('\n'+json.dumps(msg, cls=JsonEncoder, ensure_ascii=False, indent=4)+'\n')
        return msg

    def setup_prompts(self):
        super(AutoInteractor, self).setup_prompts()
        if self.config.config.goals is not None:
            self.goals=self.config.config.goals
        elif self.config.config.goals_file_path is not None:
            with open(self.config.config.goals_file_path) as file:
                self.goals=file.readlines()
        else:
            msg=self.context.user_interface.on_msg_user(Message(
                owner='system',
                content=Message.Content(text='Please input your goals:')
            ))
            self.goals=msg.content.text.split('\n')

        instruction=self.instruction\
            .replace('{ai_name}', self.cerebrum.name)\
            .replace('{ai_role}', self.cerebrum.role)\
            .replace('{ai_id}', str(self.cerebrum.id))\
            .replace('{goals}', '\n'.join([f'{i+1}. {goal}' for i, goal in enumerate(self.goals)]))

        if self.config.config.with_plugin_prompt:
            instruction=instruction.replace('{plugins}', self.plugin_manager.get_combined_prompt())

        self.instructions=[instruction]

    def setup_plugins(self):
        if not self.config.config.with_plugin_prompt:
            self.cerebrum.setup_plugins(self.plugin_manager)

    def _interact_with_cerebrum(self, command: str, message_history: List[Message], message_history_start: int, assets: Dict[str, Asset]) -> Tuple[InteractResponse, int]:
        response=self.cerebrum.interact(param=InteractParameter(
            instructions=self.instructions,
            command=command,
            message_history=message_history[message_history_start:],
            assets=[asset for asset in assets.values()],
            require_token_len=True,
            require_cost=True
        ), **self.llm_param)
        if response.input_token_len and response.input_token_len>self.summarize_token_len:
            msg_summary=self.summarizer.summarize(message_history[message_history_start:], assets[self.message_summary_key].content)
            assets[self.message_summary_key].content=msg_summary
            self.context.storage.put(self.message_summary_key, msg_summary)
            message_history_start=len(message_history)
            self.context.storage.put(self.message_history_start_key, message_history_start)
        return response, message_history_start

    def set_llm_param(self, update: Dict, remove: List):
        if update:
            self.llm_param.update(update)
        if remove:
            for key in remove:
                if key in self.llm_param:
                    self.llm_param.pop(key)

        return self.llm_param

    def command(self, command_name: str, param: Dict, **kwargs) -> Dict:
        if command_name=='set_llm_param':
            return ClassDict(param=self.set_llm_param(param.get('update'), param.get('remove')))
        else:
            raise ValueError(f'Unknown command: {command_name}. Only "set_llm_param" is acceptable.')
