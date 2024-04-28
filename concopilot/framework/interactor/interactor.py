# -*- coding: utf-8 -*-

import abc
import enum

from typing import Dict, Any

from ..plugin import AbstractPlugin, PluginManager
from ..resource import ResourceManager
from ..cerebrum import Cerebrum
from ..message.manager import MessageManager


class Interactor(AbstractPlugin):
    """
    An Interactor controls the information dispatching, task coordinating, and function calls in a copilot.
    It defines and controls the main working pipeline of specific copilots.

    During developing, generally,
    there's no need to implement `Copilot` interface for a new copilot, implement an `Interactor` interface instead.
    """

    class Status(enum.IntEnum):
        NOT_STARTED=0,
        STARTING=1,
        RUNNING=2,
        STOPPING=3,
        STOPPED=4

    def __init__(self, config: Dict):
        """
        Configure the Interactor without initialization.

        Make sure the `type` in the config file is set to "interactor".

        :param config: configures read from its config file (default to "config.yaml")
        """
        super(Interactor, self).__init__(config)
        assert self.type=='interactor'

    @abc.abstractmethod
    def setup_prompts(self):
        """
        Setup the interaction prompts if necessary.

        Setup all subcomponents' prompts here, if necessary.
        """
        pass

    @abc.abstractmethod
    def setup_plugins(self):
        """
        Setup plugins under its own scope if necessary.

        Setup all subcomponents' plugins here, if necessary.
        """
        pass

    @abc.abstractmethod
    def interact_loop(self):
        """
        The main interaction loop.

        All main procedures of the interactor/copilot tasks should be defined here.
        """
        pass

    @property
    @abc.abstractmethod
    def status(self) -> Status:
        """
        Return the status of the interactor.

        Implementations should stop and exit the interaction loop when this method returns `STOPPING` or `STOPPED`.

        :return: the status of the interactor
        """
        pass

    @status.setter
    @abc.abstractmethod
    def status(self, value: Status):
        """
        The setter of the interactor status.

        :param value: the value of the interactor status
        """
        pass

    @abc.abstractmethod
    def start(self):
        """
        Begin to start the interaction loop.
        """
        pass

    @abc.abstractmethod
    def stop(self):
        """
        Request to stop the interaction loop.
        """
        pass

    def command(self, command_name: str, param: Any, **kwargs) -> Any:
        return {}


class BasicInteractor(Interactor, metaclass=abc.ABCMeta):
    def __init__(
        self,
        config: Dict,
        resource_manager: ResourceManager,
        cerebrum: Cerebrum,
        plugin_manager: PluginManager,
        message_manager: MessageManager
    ):
        super(BasicInteractor, self).__init__(config)
        self.resource_manager: ResourceManager = resource_manager
        self.cerebrum: Cerebrum = cerebrum
        self.plugin_manager: PluginManager = plugin_manager
        self.message_manager: MessageManager = message_manager

        self._status: Interactor.Status = Interactor.Status.NOT_STARTED

    def setup_prompts(self):
        self.plugin_manager.generate_prompt()

    def setup_plugins(self):
        self.cerebrum.setup_plugins(self.plugin_manager)

    @property
    def status(self) -> Interactor.Status:
        return self._status

    @status.setter
    def status(self, value: Interactor.Status):
        self._status=value

    def start(self):
        self.status=Interactor.Status.STARTING

    def stop(self):
        self.status=Interactor.Status.STOPPING
