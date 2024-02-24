# -*- coding: utf-8 -*-

import abc

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

    def setup_prompts(self):
        self.plugin_manager.generate_prompt()

    def setup_plugins(self):
        self.cerebrum.setup_plugins(self.plugin_manager)
