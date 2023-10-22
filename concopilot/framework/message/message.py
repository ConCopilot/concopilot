# -*- coding: utf-8 -*-

from typing import Dict, Union, Any

from ...util import ClassDict
from ...util.identity import Identity


class Message(ClassDict):
    class Content(ClassDict):
        def __init__(self, command: str = None, param: Dict = None, content: Any = None, **kwargs):
            super(Message.Content, self).__init__(**kwargs)
            if command is not None:
                self.command: str = command
            if param is not None:
                self.param: ClassDict = ClassDict.convert(param)
            if content is not None:
                self.content: Any = ClassDict.convert(content) if (isinstance(content, Dict)) else content

    def __init__(self, sender: Union[Identity, Dict, str] = None, receiver: Union[Identity, Dict, str] = None, content: Dict = None, time: str = None, **kwargs):
        super(Message, self).__init__(**kwargs)
        self.sender: Union[Identity, str] = sender if sender is None or isinstance(sender, (Identity, str)) else Identity(**sender)
        self.receiver: Union[Identity, str] = receiver if receiver is None or isinstance(receiver, (Identity, str)) else Identity(**receiver)
        self.content: Message.Content = content if content is None or isinstance(content, Message.Content) else Message.Content(**content)
        self.time: str = time
