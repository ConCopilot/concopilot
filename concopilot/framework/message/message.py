# -*- coding: utf-8 -*-

import enum

from typing import Dict, Union, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ...util.context import Asset

from ...util import ClassDict
from ...util.identity import Identity


class Message(ClassDict):
    class Content(ClassDict):
        def __init__(self, *, command: str = None, param: Dict = None, data: Any = None, text: str = None, assets: Dict[str, 'Asset'] = None, **kwargs):
            """
            Message content.

            :param command: command for a plugin call
            :param param: parameter dict for a plugin call
            :param data: usually for results from plugin calls or commands, or other detailed information
            :param text: usually for user message
            :param assets: transfer assets directly if necessary, not recommended, try "context.assets" first
            :param kwargs:
            """

            super(Message.Content, self).__init__(**kwargs)
            if command is not None:
                self.command: str = command
            if param is not None:
                self.param: ClassDict = ClassDict.convert(param)
            if data is not None:
                self.data: Any = data
            if text is not None:
                self.text: str = text
            if assets is not None:
                self.assets: Dict[str, 'Asset'] = ClassDict.convert(param)

    class RetrievalMode(enum.IntEnum):
        ALL=0,
        NO_SENDER=1,
        CONTENT=2,
        INNER=3

    def __init__(self, *, sender: Union[Identity, Dict, str] = None, receiver: Union[Identity, Dict, str] = None, content: Dict = None, time: str = None, **kwargs):
        """
        Message class.

        :param sender: the message sender
        :param receiver: the message receiver. If for plugin calls, the "receiver.role" must be "plugin" and the "receiver.name" must be the plugin command name
        :param content: the message content
        :param time: the time the message to be created
        :param kwargs:
        """

        super(Message, self).__init__(**kwargs)
        if sender is not None:
            self.sender: Union[Identity, str] = sender if isinstance(sender, (Identity, str)) else Identity(**sender)
        if receiver is not None:
            self.receiver: Union[Identity, str] = receiver if isinstance(receiver, (Identity, str)) else Identity(**receiver)
        if content is not None:
            self.content: Message.Content = content if isinstance(content, Message.Content) else Message.Content(**content)
        if time is not None:
            self.time: str = time

    def retrieve(self, mode: RetrievalMode = RetrievalMode.ALL):
        if mode==Message.RetrievalMode.NO_SENDER:
            result=Message(**self)
            if 'sender' in result:
                del result.sender
        elif mode==Message.RetrievalMode.CONTENT:
            result=self.content
        elif mode==Message.RetrievalMode.INNER:
            result=self.content.text if (self.content and self.content.text is not None) else self.content
        else:
            result=self

        return result

