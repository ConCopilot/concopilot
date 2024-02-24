# -*- coding: utf-8 -*-

import enum
import uuid
import logging

from typing import Dict, Mapping, Union, Any

from ...util import ClassDict
from ...util.identity import Identity


logger=logging.getLogger('[Concopilot]')


class Message(ClassDict):
    class Command(ClassDict):
        def __init__(self,
            *,
            command: str = None,
            param: Any = None,
            response: Any = None,
            **kwargs
        ):
            """
            Message content.

            :param command: command name for a plugin call
            :param param: command parameter for a plugin call
            :param response: results from a plugin call
            :param kwargs:
            """
            super(Message.Command, self).__init__(**kwargs)
            if command is not None:
                self.command: str = command
            if param is not None:
                self.param: Any = ClassDict.convert(param) if isinstance(param, Mapping) else param
            if response is not None:
                self.response: Any = ClassDict.convert(response) if isinstance(response, Mapping) else param

    class RetrievalMode(enum.IntEnum):
        ALL=0,
        NO_SENDER=1,
        CONTENT_INFO=2,
        CONTENT=3

    def __init__(
        self,
        *,
        sender: Union[Identity, Dict, str] = None,
        receiver: Union[Identity, Dict, str] = None,
        content_type: str = None,
        content: Any = None,
        time: str = None,
        id: Union[uuid.UUID, str, int] = None,
        thrd_id: Union[uuid.UUID, str, int] = None,
        **kwargs
    ):
        """
        Message class.

        :param sender: the message sender
        :param receiver: the message receiver. If for plugin calls, the "receiver.role" must be "plugin" and the "receiver.name" must be the plugin command name
        :param content_type: the message content type
        :param content: the message content
        :param time: the time the message to be created
        :param id: an optional id of this message
        :param thrd_id: an optional id for a message thread that this message belongs to.
        :param kwargs:
        """

        super(Message, self).__init__(**kwargs)
        if sender is not None:
            self.sender: Union[Identity, str] = sender if isinstance(sender, Identity) else (Identity(role=sender) if isinstance(sender, str) else Identity(**ClassDict.convert(sender)))
        if receiver is not None:
            self.receiver: Union[Identity, str] = receiver if isinstance(receiver, Identity) else (Identity(role=receiver) if isinstance(receiver, str) else Identity(**ClassDict.convert(receiver)))
        if content_type is not None:
            self.content_type: str = content_type
        if content is not None:
            if isinstance(content, Mapping):
                content=ClassDict.convert(content)
                if content.command:
                    content=Message.Command(**content)
            self.content: Any = content
        if time is not None:
            self.time: str = time
        if id is not None:
            self.id: Union[uuid.UUID, str, int] = id
        if thrd_id is not None:
            self.thrd_id: Union[uuid.UUID, str, int] = thrd_id

    def retrieve(self, mode: RetrievalMode = RetrievalMode.ALL):
        if mode is None or mode==Message.RetrievalMode.ALL:
            result=self
        elif mode==Message.RetrievalMode.NO_SENDER:
            result=Message(**self)
            if 'sender' in result:
                del result.sender
        elif mode==Message.RetrievalMode.CONTENT_INFO:
            result=Message(content_type=self.content_type, content=self.content)
        elif mode==Message.RetrievalMode.CONTENT:
            result=self.content
        else:
            logger.warning(f'Unknown message retrieve mode: `{mode}`')
            result=self

        return result
