# -*- coding: utf-8 -*-

import abc

from typing import Optional

from .interface import UserInterface
from ..message import Message
from ...util.error import ConCopilotError


class AgentDrivenSimplexUserInterface(UserInterface, metaclass=abc.ABCMeta):
    def send_msg_to_agent(self, msg: Message):
        raise ConCopilotError('This method is unsupported in an Agent-Driven simplex user interface!')

    def on_msg_to_agent(self, msg: Message) -> Optional[Message]:
        raise ConCopilotError('This method is unsupported in an Agent-Driven simplex user interface!')

    def has_agent_msg(self) -> bool:
        raise ConCopilotError('This method is unsupported in an Agent-Driven simplex user interface!')

    def get_agent_msg(self) -> Optional[Message]:
        raise ConCopilotError('This method is unsupported in an Agent-Driven simplex user interface!')

    def wait_agent_msg(self) -> Optional[Message]:
        raise ConCopilotError('This method is unsupported in an Agent-Driven simplex user interface!')


class UserDrivenSimplexUserInterface(UserInterface, metaclass=abc.ABCMeta):
    def send_msg_to_user(self, msg: Message):
        raise ConCopilotError('This method is unsupported in an User-Driven simplex user interface!')

    def on_msg_to_user(self, msg: Message) -> Optional[Message]:
        raise ConCopilotError('This method is unsupported in an User-Driven simplex user interface!')

    def has_user_msg(self) -> bool:
        raise ConCopilotError('This method is unsupported in an User-Driven simplex user interface!')

    def get_user_msg(self) -> Optional[Message]:
        raise ConCopilotError('This method is unsupported in an User-Driven simplex user interface!')

    def wait_user_msg(self) -> Optional[Message]:
        raise ConCopilotError('This method is unsupported in an User-Driven simplex user interface!')
