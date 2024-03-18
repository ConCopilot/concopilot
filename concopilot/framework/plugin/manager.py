# -*- coding: utf-8 -*-

import abc
import uuid

from typing import Dict, Union, List, Optional, Any

from ..plugin.plugin import Plugin, AbstractPlugin
from .promptgenerator import PluginPromptGenerator
from ..resource import ResourceManager
from ..context import Context
from ...util.initializer import component


class PluginManager(AbstractPlugin):
    """
    Manager all plugins in a copilot,
    including adding, holding, indexing, initializing plugins, and generate prompts for those plugins if necessary.
    """

    def __init__(self, config: Dict):
        """
        Configure the PluginManager without initialization.

        Make sure the `type` in the config file is set to "plugin_manager".

        :param config: configures read from its config file (default to "config.yaml")
        """
        super(PluginManager, self).__init__(config)
        assert self.type=='plugin_manager'

    def config_resources(self, resource_manager: ResourceManager):
        super(PluginManager, self).config_resources(resource_manager)
        self.plugin_prompt_generator.config_resources(resource_manager)
        for plugin in self.plugins:
            plugin.config_resources(resource_manager)

    def config_context(self, context: Context):
        super(PluginManager, self).config_context(context)
        self.plugin_prompt_generator.config_context(context)
        for plugin in self.plugins:
            plugin.config_context(context)

    @abc.abstractmethod
    def generate_prompt(self):
        """
        Generate prompt for itself and managed plugins if necessary.
        """
        pass

    @abc.abstractmethod
    def get_combined_prompt(self) -> str:
        """
        Return the combined prompt of itself and all plugins managed.

        :return: the combined prompt string
        """
        pass

    @property
    @abc.abstractmethod
    def plugin_prompt_generator(self) -> PluginPromptGenerator:
        """
        Get the plugin_prompt_generator object.

        :return: the plugin_prompt_generator
        """
        pass

    @plugin_prompt_generator.setter
    @abc.abstractmethod
    def plugin_prompt_generator(self, value: PluginPromptGenerator):
        """
        Set the plugin_prompt_generator object.

        :param value: the new plugin_prompt_generator
        """
        pass

    @property
    @abc.abstractmethod
    def plugins(self) -> List[Plugin]:
        """
        :return: the full list of managed plugins
        """
        pass

    @property
    @abc.abstractmethod
    def plugin_id_map(self) -> Dict[Union[uuid.UUID, str, int], Plugin]:
        """
        :return: the map of managed plugins arranged by the plugin id
        """
        pass

    @property
    @abc.abstractmethod
    def plugin_name_map(self) -> Dict[str, Plugin]:
        """
        :return: the map of managed plugins arranged by the plugin name
        """
        pass

    @abc.abstractmethod
    def add_plugin(self, plugin: Plugin):
        """
        Add a new plugin to the plugin pool.

        :param plugin: the new plugin to be added
        """
        pass

    def get_plugin(self, *, id: Union[uuid.UUID, str, int] = None, name: str = None) -> Optional[Plugin]:
        """
        Retrieve a plugin with its id and name.

        :param id: the plugin id
        :param name: the plugin name
        :return: the plugin found or None
        """
        if id:
            plugin=self.plugin_id_map.get(id)
            if plugin and name and plugin.name!=name:
                return None
            return plugin
        elif name is not None:
            return self.plugin_name_map.get(name)
        else:
            return None

    def command(self, command_name: str, param: Any, **kwargs) -> Any:
        return {}


class BasicPluginManager(PluginManager):
    def __init__(self, config: Dict):
        super(BasicPluginManager, self).__init__(config)
        self._plugin_prompt_generator: PluginPromptGenerator
        if self.config.config.plugin_prompt_generator is not None:
            self.plugin_prompt_generator=component.create_component(self.config.config.plugin_prompt_generator)
        elif self.config.plugin_prompt_generator is not None:
            self.plugin_prompt_generator=component.create_component(self.config.plugin_prompt_generator)
        self._plugins: List[Plugin] = []
        self._plugin_id_map: Dict[Union[uuid.UUID, str, int], Plugin] = {}
        self._plugin_name_map: Dict[str, Plugin] = {}
        if self.config.plugins is not None:
            for plugin_config in self.config.plugins:
                plugin=component.create_component(plugin_config)
                self.add_plugin(plugin)
        if self.config.config.plugins is not None:
            for plugin_config in self.config.config.plugins:
                plugin=component.create_component(plugin_config)
                self.add_plugin(plugin)

    def generate_prompt(self):
        for plugin in self.plugins:
            if plugin.prompt is None or len(plugin.prompt)==0:
                plugin.prompt=self.plugin_prompt_generator.generate_prompt(plugin)

    def get_combined_prompt(self) -> str:
        return '\n\n'.join([plugin.prompt for plugin in self.plugins])

    @property
    def plugin_prompt_generator(self) -> PluginPromptGenerator:
        return self._plugin_prompt_generator

    @plugin_prompt_generator.setter
    def plugin_prompt_generator(self, value: PluginPromptGenerator):
        self._plugin_prompt_generator=value

    @property
    def plugins(self) -> List[Plugin]:
        return self._plugins

    @property
    def plugin_id_map(self) -> Dict[Union[uuid.UUID, str, int], Plugin]:
        return self._plugin_id_map

    @property
    def plugin_name_map(self) -> Dict[str, Plugin]:
        return self._plugin_name_map

    def add_plugin(self, plugin: Plugin):
        assert plugin.config.as_plugin==True
        assert plugin.id is not None
        assert plugin.name is not None
        assert plugin.config.info is not None
        assert plugin.config.commands is not None and len(plugin.config.commands)>0
        if plugin.id in self.plugin_id_map:
            existed=self.plugin_id_map[plugin.id]
            raise ValueError(f'\
                Plugin with id={plugin.id} already existed.\
                \n    Existed: ({existed.group_id}, {existed.group_id}, {existed.group_id})\
                \n    Current: ({plugin.group_id}, {plugin.group_id}, {plugin.group_id})\
                You can modify the id in the "config" field in the plugin config.yaml file\
            ')
        if plugin.name in self.plugin_name_map:
            existed=self.plugin_name_map[plugin.name]
            raise ValueError(f'\
                Plugin with name={plugin.name} already existed.\
                \n    Existed: ({existed.group_id}, {existed.group_id}, {existed.group_id})\
                \n    Current: ({plugin.group_id}, {plugin.group_id}, {plugin.group_id})\
                You can modify the name in the "config" field in the plugin config.yaml file\
            ')
        self.plugins.append(plugin)
        self.plugin_id_map[plugin.id]=plugin
        self.plugin_name_map[plugin.name]=plugin

    def command(self, command_name: str, param: Any, **kwargs) -> Any:
        return {}
