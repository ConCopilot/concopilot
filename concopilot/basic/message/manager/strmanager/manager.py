# -*- coding: utf-8 -*-

import logging

from typing import List, Dict, Any

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

    def parse(self, response: InteractResponse) -> List[Message]:
        msg_list=[]
        if response.content:
            msg_list.append(Message(
                content_type='text/plain',
                content=response.content,
                time=settings.current_time(),
            ))
        if response.plugin_call:
            msg_list.append(Message(
                receiver=Identity(
                    role='plugin',
                    name=response.plugin_call.plugin_name
                ),
                content_type='command',
                content=Message.Command(
                    command=response.plugin_call.command,
                    param=response.plugin_call.param
                ),
                time=settings.current_time(),
            ))
        return msg_list

    def command(self, command_name: str, param: Any, **kwargs) -> Any:
        return {}
