# -*- coding: utf-8 -*-

import uuid
import logging

from typing import List, Dict, Union, Any

from .....framework.message import Message
from .....framework.message.manager import MessageManager
from .....framework.cerebrum import InteractResponse
from .....framework.identity import Identity
from .....package.config import Settings


settings=Settings()
logger=logging.getLogger(__file__)


class BasicStrMessageManager(MessageManager):
    def __init__(self, config: Dict):
        super(BasicStrMessageManager, self).__init__(config)

    def parse(self, response: InteractResponse, thrd_id: Union[uuid.UUID, str, int] = None) -> List[Message]:
        msg_list=[]
        if response.content:
            msg_list.append(Message(
                content_type='text/plain',
                content=response.content,
                time=settings.current_time(),
                thrd_id=thrd_id
            ))
        if response.plugin_calls:
            for plugin_call in response.plugin_calls:
                content=Message.Command(**plugin_call)
                msg_list.append(Message(
                    receiver=Identity(
                        role='plugin',
                        name=content.pop('plugin_name', None)
                    ),
                    content_type='command',
                    content=content,
                    time=settings.current_time(),
                    thrd_id=thrd_id
                ))
        return msg_list

    def command(self, command_name: str, param: Any, **kwargs) -> Any:
        return {}
