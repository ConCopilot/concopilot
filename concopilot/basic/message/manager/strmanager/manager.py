# -*- coding: utf-8 -*-

import logging

from typing import Dict

from concopilot.framework.message import Message
from concopilot.framework.message.manager import MessageManager
from concopilot.framework.cerebrum import InteractResponse
from concopilot.util.identity import Identity
from concopilot.package.config import Settings

settings=Settings()
logger=logging.getLogger(__file__)


class BasicStrMessageManager(MessageManager):
    def __init__(self, config: Dict):
        super(BasicStrMessageManager, self).__init__(config)

    def parse(self, response: InteractResponse) -> Message:
        receiver=None
        content=None
        if response.content:
            content=Message.Content(text=response.content)
        if response.plugin_call:
            receiver=Identity(
                role='plugin',
                name=response.plugin_call.plugin_name
            )
            content=Message.Content(
                command=response.plugin_call.command,
                param=response.plugin_call.param
            )
        return Message(
            sender=None,
            receiver=receiver,
            content=content,
            time=settings.current_time(),
        )

    def command(self, command_name: str, param: Dict, **kwargs) -> Dict:
        return {}
