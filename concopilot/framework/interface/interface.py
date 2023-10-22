# -*- coding: utf-8 -*-

import abc

from typing import Dict, Optional

from ..plugin import AbstractPlugin
from ..message import Message


class UserInterface(AbstractPlugin):
    """
    The common interface to deal with interactions with user.
    """

    def __init__(self, config: Dict):
        """
        Configure the UserInterface without initialization.

        Make sure the `type` in the config file is set to "user_interface".

        :param config: configures read from its config file (default to "config.yaml")
        """
        super(UserInterface, self).__init__(config)
        assert self.type=='user_interface'

    @abc.abstractmethod
    def send_user_msg(self, msg: Message):
        """
        Send a message to the user.

        :param msg: the message to be sent
        """
        pass

    @abc.abstractmethod
    def on_user_msg(self, msg: Message) -> Message:
        """
        Send a message to the user and wait the user response.

        :param msg: the message to be sent
        :return: the message return by the user
        """
        pass

    @abc.abstractmethod
    def has_user_msg(self) -> bool:
        """
        Check if user has sent any message.

        :return: True if there is any message from the user, otherwise False
        """
        pass

    @abc.abstractmethod
    def get_user_msg(self) -> Optional[Message]:
        """
        Retrieve a new user message if any.

        :return: the first message from the user, otherwise None
        """
        pass

    def command(self, command_name: str, param: Dict, **kwargs) -> Dict:
        return {}
