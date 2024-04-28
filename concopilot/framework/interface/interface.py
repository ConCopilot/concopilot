# -*- coding: utf-8 -*-

import abc

from typing import Dict, Optional, Any

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
    def send_msg_to_user(self, msg: Message):
        """
        Send a message to the user.

        :param msg: the message to be sent
        """
        pass

    @abc.abstractmethod
    def on_msg_to_user(self, msg: Message) -> Optional[Message]:
        """
        Send a message to the user and wait the user response.

        This method must return the exact response to the input `msg`.
        Implementations may need to take special mechanism to guarantee this.

        :param msg: the message to be sent
        :return: the message return by the user, None if the user want to stop the pipeline
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

        :return: the first message from the user, None if there is no user message currently
        """
        pass

    @abc.abstractmethod
    def wait_user_msg(self) -> Optional[Message]:
        """
        Wait for a new user message.

        :return: the first message from the user, None if the user want to stop the pipeline
        """
        pass

    @abc.abstractmethod
    def send_msg_to_agent(self, msg: Message):
        """
        Send a message to the agent.

        :param msg: the message to be sent
        """
        pass

    @abc.abstractmethod
    def on_msg_to_agent(self, msg: Message) -> Optional[Message]:
        """
        Send a message to the agent and wait the agent response.

        This method must return the exact response to the input `msg`.
        Implementations may need to take special mechanism to guarantee this.

        :param msg: the message to be sent
        :return: the message return by the agent, None if the agent want to stop the pipeline
        """
        pass

    @abc.abstractmethod
    def has_agent_msg(self) -> bool:
        """
        Check if agent has sent any message.

        :return: True if there is any message from the agent, otherwise False
        """
        pass

    @abc.abstractmethod
    def get_agent_msg(self) -> Optional[Message]:
        """
        Retrieve a new agent message if any.

        :return: the first message from the agent, None if there is no agent message currently
        """
        pass

    @abc.abstractmethod
    def wait_agent_msg(self) -> Optional[Message]:
        """
        Wait for a new agent message.

        :return: the first message from the agent, None if the user want to stop the pipeline
        """
        pass

    @abc.abstractmethod
    def interrupt(self):
        """
        Interrupt the waiting of all progresses in this `UserInterface` object,
        and shut down the message pipeline.
        An `InterruptedError` should be raised from threads in which any progress is waiting.
        """
        pass

    @property
    @abc.abstractmethod
    def interrupted(self) -> bool:
        """
        Indicates if current `UserInterface` object has been interrupted.
        No further message should be processed if current object has been interrupted.

        :return: True if current object has been interrupted, otherwise False
        """
        pass

    def command(self, command_name: str, param: Any, **kwargs) -> Any:
        return {}
