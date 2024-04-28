# -*- coding: utf-8 -*-

import abc
import threading

from typing import List, Dict, Any

from .plugin import AbstractPlugin, PluginManager
from .resource import ResourceManager
from .cerebrum import Cerebrum
from .storage import Storage
from .interface import UserInterface
from .message.manager import MessageManager
from .interactor import Interactor
from .resource import Resource
from .context import Context
from ..util.initializer import component
from ..util import ClassDict


class Copilot(AbstractPlugin):
    """
    Define the Copilot interface.

    All copilots implement the Plugin interface, so it is easy to use a copilot as a plugin in another copilot.
    """

    def __init__(self, config: Dict):
        """
        Configure the copilot without initialization.

        Make sure the `type` in the config file is set to "copilot" or "agent".

        :param config: configures read from its config file (default to "config.yaml")
        """
        super(Copilot, self).__init__(config)
        assert self.type=='copilot' or self.type=='agent'

    @abc.abstractmethod
    def config_copilot_resources(self):
        pass

    @abc.abstractmethod
    def config_copilot_context(self):
        pass

    @property
    @abc.abstractmethod
    def copilot_context(self):
        pass

    @abc.abstractmethod
    def initialize_copilot(self):
        """
        Initialize the framework and resources
        """
        pass

    @abc.abstractmethod
    def finalize_copilot(self):
        """
        Finalize the framework and resources.
        """
        pass

    @abc.abstractmethod
    def run_interaction(self):
        """
        Run the copilot/agent interaction.

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

    def command(self, command_name: str, param: Any, **kwargs) -> Any:
        """
        The Plugin command method.

        Ignore this method if you are not expecting your copilot/agent acting as a plugin in other copilots/agents,
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
        self.resource_manager: ResourceManager = component.create_component(self.config.config.resource_manager) if self.config.config.resource_manager else None
        self.storage: Storage = component.create_component(self.config.config.storage) if self.config.config.storage else None
        self.user_interface: UserInterface = component.create_component(self.config.config.user_interface) if self.config.config.user_interface else None
        self.cerebrum: Cerebrum = component.create_component(self.config.config.cerebrum) if self.config.config.cerebrum else None
        self.plugin_manager: PluginManager = component.create_component(self.config.config.plugin_manager) if self.config.config.plugin_manager else None
        self.message_manager: MessageManager = component.create_component(self.config.config.message_manager) if self.config.config.message_manager else None

        self.interactor: Interactor = component.create_component(
            self.config.config.interactor,
            self.resource_manager,
            self.cerebrum,
            self.plugin_manager,
            self.message_manager
        ) if self.config.config.interactor else None

        self._outer_resources: List[Resource] = None
        self._copilot_context: Context = None
        self._running: threading.Event = threading.Event()
        self._running_thrd: threading.Thread = None

    def config_resources(self, resource_manager: ResourceManager):
        super(BasicCopilot, self).config_resources(resource_manager)
        if self.config.config.inherit_resources and resource_manager:
            self._outer_resources=resource_manager.resources

    def config_copilot_resources(self):
        if self.storage:
            self.storage.config_resources(self.resource_manager)
        if self.user_interface:
            self.user_interface.config_resources(self.resource_manager)
        if self.cerebrum:
            self.cerebrum.config_resources(self.resource_manager)
        if self.plugin_manager:
            self.plugin_manager.config_resources(self.resource_manager)
        if self.message_manager:
            self.message_manager.config_resources(self.resource_manager)
        if self.interactor:
            self.interactor.config_resources(self.resource_manager)

    def config_copilot_context(self):
        self._copilot_context=Context(
            storage=self.storage,
            assets=ClassDict(),
            user_interface=self.user_interface
        )
        if self.resource_manager:
            self.resource_manager.config_context(self._copilot_context)
        if self.storage:
            self.storage.config_context(self._copilot_context)
        if self.user_interface:
            self.user_interface.config_context(self._copilot_context)
        if self.cerebrum:
            self.cerebrum.config_context(self._copilot_context)
        if self.plugin_manager:
            self.plugin_manager.config_context(self._copilot_context)
        if self.message_manager:
            self.message_manager.config_context(self._copilot_context)
        if self.interactor:
            self.interactor.config_context(self._copilot_context)

    @property
    def copilot_context(self):
        return self._copilot_context

    def initialize_copilot(self):
        if self.resource_manager:
            self.resource_manager.initialize()
            if self.config.config.inherit_resources and self._outer_resources is not None:
                for resource in self._outer_resources:
                    self.resource_manager.add_resource(resource)
            elif self.config.config.inherit_self_resources:
                for resource in self.resources:
                    self.resource_manager.add_resource(resource)
            self.config_copilot_resources()
        self.config_copilot_context()
        if self.plugin_manager:
            self.plugin_manager.initialize()
        if self.interactor:
            self.interactor.setup_prompts()
            self.interactor.setup_plugins()

    def finalize_copilot(self):
        if self.plugin_manager:
            self.plugin_manager.finalize()
        if self.resource_manager:
            self.resource_manager.finalize()

    def run_interaction(self):
        self._running.set()
        if self.interactor:
            self.interactor.start()
            self.interactor.interact_loop()
        else:
            raise ValueError('No interactor configured!')

    def initialize(self):
        super(BasicCopilot, self).initialize()
        self._running_thrd=threading.Thread(target=self.run)
        self._running_thrd.start()
        self._running.wait()

    def finalize(self):
        if self._running_thrd:
            self._running.wait()
            self.interactor.stop()
            self.user_interface.interrupt()
            self._running_thrd.join()
        super(BasicCopilot, self).finalize()

    def run(self):
        self.initialize_copilot()
        self.run_interaction()
        self.finalize_copilot()


Agent=Copilot
BasicAgent=BasicCopilot
