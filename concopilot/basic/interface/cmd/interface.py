# -*- coding: utf-8 -*-

import json

from typing import Dict, Optional

from ....framework.interface import UserInterface
from ....framework.message import Message
from ....util.jsons import JsonEncoder
from ....package.config import Settings


settings=Settings()


class CmdUserInterface(UserInterface):
    def __init__(self, config: Dict):
        super(CmdUserInterface, self).__init__(config)
        self.default_request_prompt: str = self.config.config.default_request_prompt if self.config.config.default_request_prompt else 'Waiting for your input:'
        self.default_received_prompt: str = self.config.config.default_received_prompt if self.config.config.default_received_prompt else 'Your message received.'
        self.multiple_line_input: str=self.config.config.multiple_line_input

    def send_user_msg(self, msg: Message):
        print(json.dumps(msg, cls=JsonEncoder, ensure_ascii=False, indent=4))

    def on_user_msg(self, msg: Message) -> Message:
        print(msg.content.content if msg.content else self.default_request_prompt)
        content=self._input()
        print(self.default_received_prompt)
        return Message(
            sender=msg.receiver,
            receiver=msg.sender,
            content=Message.Content(content=content),
            time=settings.current_time()
        )

    def has_user_msg(self) -> bool:
        return False

    def get_user_msg(self) -> Optional[Message]:
        return None

    def _input(self) -> str:
        content=[]
        while True:
            line=input()
            if not self.multiple_line_input or line=='':
                break
            content.append(line)
        return '\n'.join(content)
