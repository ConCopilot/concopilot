# -*- coding: utf-8 -*-

import abc

from typing import Dict

from .plugin import AbstractPlugin, PluginManager
from .resource import ResourceManager
from .cerebrum import Cerebrum
from .storage import Storage
from .interface import UserInterface
from .message.manager import MessageManager
from .interactor import Interactor
from ..util.initializer import component
from ..util.context import Context
from ..util import ClassDict


class Copilot(AbstractPlugin):
    """
    Define the Copilot interface.

    All copilots implement the Plugin interface, so it is easy to use a copilot as a plugin in another copilot.
    """

    def __init__(self, config: Dict):
        """
        Configure the copilot without initialization.

        Make sure the `type` in the config file is set to "copilot".

        :param config: configures read from its config file (default to "config.yaml")
        """
        super(Copilot, self).__init__(config)
        assert self.type=='copilot'

    @abc.abstractmethod
    def initialize(self):
        """
        Initialize the framework and resources
        """
        pass

    @abc.abstractmethod
    def finalize(self):
        """
        Finalize the framework and resources
        """
        pass

    @abc.abstractmethod
    def run_interaction(self):
        """
        Run the copilot interaction.

        This is the main logic of the copilot,
        so write your special task pipeline here.
        """
        pass

    @abc.abstractmethod
    def run(self):
        """
        The entrance of the copilot task pipeline.

        This method does the initialization, runs the interaction, and does the finalization.
        """
        pass

    def command(self, command_name: str, param: Dict, **kwargs) -> Dict:
        """
        The Plugin command method.

        Ignore this method if you are not expect your copilot acting as a plugin in other copilots,
        or you have to override it as the same way of which in developing Plugins.

        :param command_name: command name
        :param param: command parameters
        :param kwargs: reserved, not recommend to use
        :return: the command result
        """
        return {}


class BasicCopilot(Copilot):
    def __init__(self, config: Dict):
        super(BasicCopilot, self).__init__(config)
        self.resource_manager: ResourceManager = component.create_component(self.config.config.resource_manager)
        self.storage: Storage = component.create_component(self.config.config.storage)
        self.user_interface: UserInterface = component.create_component(self.config.config.user_interface)
        self.cerebrum: Cerebrum = component.create_component(self.config.config.cerebrum)
        self.plugin_manager: PluginManager = component.create_component(self.config.config.plugin_manager)
        self.message_manager: MessageManager = component.create_component(self.config.config.message_manager)

        self.interactor: Interactor = component.create_component(
            self.config.config.interactor,
            self.resource_manager,
            self.cerebrum,
            self.plugin_manager,
            self.message_manager
        )

    def config_resources(self, resource_manager: ResourceManager):
        super(BasicCopilot, self).config_resources(resource_manager)
        self.storage.config_resources(resource_manager)
        self.user_interface.config_resources(resource_manager)
        self.cerebrum.config_resources(resource_manager)
        self.plugin_manager.config_resources(resource_manager)
        self.message_manager.config_resources(resource_manager)
        self.interactor.config_resources(resource_manager)

    def config_context(self, context: Context):
        super(BasicCopilot, self).config_context(context)
        self.resource_manager.config_context(context)
        self.storage.config_context(context)
        self.user_interface.config_context(context)
        self.cerebrum.config_context(context)
        self.plugin_manager.config_context(context)
        self.message_manager.config_context(context)
        self.interactor.config_context(context)

    def initialize(self):
        self.resource_manager.initialize()
        self.config_resources(self.resource_manager)
        self.config_context(Context(
            storage=self.storage,
            assets=ClassDict(),
            user_interface=self.user_interface
        ))
        self.interactor.setup_prompts()
        self.interactor.setup_plugins()

    def finalize(self):
        self.resource_manager.finalize()

    def run_interaction(self):
        self.interactor.interact_loop()

    def run(self):
        self.initialize()
        self.run_interaction()
        self.finalize()
