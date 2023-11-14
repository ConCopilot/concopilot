# -*- coding: utf-8 -*-

import json
import time

from typing import Optional

from concopilot.framework.plugin import PluginManager
from concopilot.framework.cerebrum import InteractParameter, InteractResponse, AbstractCerebrum
from concopilot.framework.resource.category.model import LLM
from concopilot.framework.message import Message
from concopilot.util.jsons import JsonEncoder


class RWKVCerebrum(AbstractCerebrum):
    def __init__(self, config):
        super(RWKVCerebrum, self).__init__(config)
        self._model: LLM = None
        self.max_tokens: int = self.config.config.max_tokens
        self.msg_retrieval_mode: Message.RetrievalMode = Message.RetrievalMode[self.config.config.msg_retrieval_mode.upper()]
        self._instruction_prompt: str = f'Make your response less than {self.max_tokens} tokens.' if self.max_tokens>0 else None
        self._plugin_prompt: str = None

    def setup_plugins(self, plugin_manager: PluginManager):
        if plugin_manager is not None:
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
        if param.content:
            prompt_list=[param.content, f"The current time and date is {time.strftime('%c')}"]
            if self._plugin_prompt is not None:
                prompt_list.insert(-1, self._plugin_prompt)

            if self.instruction_prompt():
                prompt_list.append(self.instruction_prompt())
            if param.command:
                prompt_list.append(param.command)
        else:
            prompt_list=param.instructions+[f"The current time and date is {time.strftime('%c')}"]
            if self._plugin_prompt is not None:
                prompt_list.insert(-1, self._plugin_prompt)

            if self.instruction_prompt():
                prompt_list.append(self.instruction_prompt())

            if param.message_history is not None and len(param.message_history)>0:
                prompt_list.append('Below are interaction messages between you, plugins, and the user so far:')
                for msg in param.message_history:
                    content=msg.retrieve(self.msg_retrieval_mode)
                    if not isinstance(content, str):
                        content=json.dumps(content, cls=JsonEncoder, ensure_ascii=False)
                    prompt_list.append(content)

            if param.assets is not None and len(param.assets)>0:
                prompt_list.append('Below are assets for your reference:\n\n'+json.dumps(param.assets, cls=JsonEncoder, ensure_ascii=False))

            if param.content:
                prompt_list.append(param.content)

            if param.command:
                prompt_list.append(param.command)

        reply=self.model.inference({
            'prompt': '\n\n'.join(prompt_list),
            'max_tokens': self.max_tokens,
            'require_token_len': param.require_token_len,
            'require_cost': param.require_cost
        }, **kwargs)

        return InteractResponse(**reply)
