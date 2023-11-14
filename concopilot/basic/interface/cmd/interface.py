# -*- coding: utf-8 -*-

from typing import Dict, Optional

from ....framework.interface import UserInterface
from ....framework.message import Message
from ....package.config import Settings


settings=Settings()


class CmdUserInterface(UserInterface):
    def __init__(self, config: Dict):
        super(CmdUserInterface, self).__init__(config)
        self.user_msg_prefix: str = self.config.config.user_msg_prefix if self.config.config.user_msg_prefix else ''
        self.user_msg_suffix: str = self.config.config.user_msg_suffix if self.config.config.user_msg_suffix else ''
        self.non_user_msg_prefix: str = self.config.config.non_user_msg_prefix if self.config.config.non_user_msg_prefix else ''
        self.non_user_msg_suffix: str = self.config.config.non_user_msg_suffix if self.config.config.non_user_msg_suffix else ''
        self.multiple_line_input: bool = self.config.config.multiple_line_input

        self.last_sender=None
        self.last_receiver=None

    def send_msg_user(self, msg: Message):
        print(self.non_user_msg_prefix)
        print(msg.content.text if msg.content else '')
        print(self.non_user_msg_suffix)
        self.last_sender=msg.sender
        self.last_receiver=msg.receiver

    def has_user_msg(self) -> bool:
        return False

    def get_user_msg(self) -> Optional[Message]:
        return None

    def wait_user_msg(self) -> Optional[Message]:
        print(self.user_msg_prefix)
        text=self._input()
        print(self.user_msg_suffix)
        return Message(
            sender=self.last_receiver,
            receiver=self.last_sender,
            content=Message.Content(text=text),
            time=settings.current_time()
        )

    def _input(self) -> str:
        texts=[]
        while True:
            line=input()
            if line:
                texts.append(line)
            if not self.multiple_line_input or not line:
                break
        return '\n'.join(texts)
