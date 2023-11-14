# -*- coding: utf-8 -*-

import logging

from typing import Dict, List

from concopilot.framework.plugin import PluginManager
from concopilot.framework.interactor import BasicInteractor
from concopilot.framework.resource import ResourceManager
from concopilot.framework.cerebrum import InteractParameter, Cerebrum
from concopilot.framework.message import Message
from concopilot.framework.message.manager import MessageManager
from concopilot.util.identity import Identity
from concopilot.util import ClassDict
from concopilot import Settings


settings=Settings()
logger=logging.getLogger(__file__)


class ChatInteractor(BasicInteractor):
    def __init__(
        self,
        config: Dict,
        resource_manager: ResourceManager,
        cerebrum: Cerebrum,
        plugin_manager: PluginManager,
        message_manager: MessageManager
    ):
        super(ChatInteractor, self).__init__(
            config,
            resource_manager,
            cerebrum,
            plugin_manager,
            message_manager
        )
        self.persist_history: bool = self.config.config.persist_history
        self.message_history_key=self.config.config.message_history_key
        self.hello_msg_role: str = self.config.config.hello_msg_role
        self.hello_msg_content: str = self.config.config.hello_msg_content
        self.instructions: List[str] = []
        if self.config.config.instruction_file:
            with open(self.config_file_path(self.config.config.instruction_file)) as file:
                self.instructions.append(file.read())
        self.exit_tokens: set[str] = set(self.config.config.exit_tokens)
        self.llm_param={}

    def interact_loop(self):
        message_history: List[Message] = self.context.storage.get_or_default(self.message_history_key, []) if self.persist_history else []

        if len(message_history)>0:
            msg=message_history[-1]
            if message_history[-1].sender.role=='user':
                message_history=message_history[:-1]
                msg=self._interact_with_cerebrum(msg, message_history)
        else:
            msg=Message(
                sender=Identity(role=self.hello_msg_role),
                receiver=Identity(role='user'),
                content=Message.Content(text=self.hello_msg_content),
                time=settings.current_time()
            )
        while True:
            try:
                self.context.user_interface.send_msg_user(msg)
                msg=self._check_user_msg()
                if msg is None or msg.content.text in self.exit_tokens:
                    break
                msg=self._interact_with_cerebrum(msg, message_history)
            except Exception as e:
                logger.error('An error happened.', exc_info=e)
                msg=Message(
                    sender=Identity(role='system'),
                    receiver=Identity(role='user'),
                    content=Message.Content(
                        text=f'{str(e.__class__.__name__)}: {str(e)}'
                    )
                )

        if self.persist_history:
            self.context.storage.put(self.message_history_key, message_history)

    def _check_user_msg(self):
        while msg:=self.context.user_interface.wait_user_msg():
            if msg is not None:
                if msg.receiver and msg.receiver.role=='interactor' and msg.content:
                    self.command(command_name=msg.content.command, param=msg.content.param)
                else:
                    break
            else:
                logger.error('User interface pipeline is broken. Will exit.')
                break
        return msg

    def _interact_with_cerebrum(self, msg, message_history):
        response=self.cerebrum.interact(param=InteractParameter(
            instructions=self.instructions,
            command=msg.content.text,
            message_history=message_history,
            assets=[asset for asset in self.context.assets.values()],
            require_token_len=False,
            require_cost=False
        ), **self.llm_param)
        message_history.append(msg)
        msg=self.message_manager.parse(response)
        msg.sender=Identity(role='cerebrum', id=self.cerebrum.id, name=self.cerebrum.name)
        if msg.receiver is None:
            msg.receiver=Identity(role='user')
        message_history.append(msg)
        return msg

    def setup_plugins(self):
        pass

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
