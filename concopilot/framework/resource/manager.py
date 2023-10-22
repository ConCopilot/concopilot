# -*- coding: utf-8 -*-

import abc
import uuid

from typing import Dict, Union, List

from ..resource import Resource
from ..plugin import AbstractPlugin
from ...util.initializer import component
from ...util.context import Context


class ResourceManager(AbstractPlugin):
    """
    Manage and maintain Resources,
    including adding and holding resources, as well as initialize and finalize resources.

    Any specific resource can only be used by a plugin after being initialized in a resource manager.
    """

    def __init__(self, config: Dict):
        """
        Configure the ResourceManager without initialization.

        Make sure the `type` in the config file is set to "resource_manager".

        :param config: configures read from its config file (default to "config.yaml")
        """
        super(ResourceManager, self).__init__(config)
        assert self.type=='resource_manager'

    @abc.abstractmethod
    def add_resource(self, resource: Resource):
        """
        Add a new resource to the resource pool.

        :param resource:the new resource to be added
        """
        pass

    def config_resources(self, resource_manager: 'ResourceManager'):
        pass

    def config_context(self, context: Context):
        super(ResourceManager, self).config_context(context)
        for resource in self.resources:
            resource.config_context(context)

    @abc.abstractmethod
    def initialize(self):
        """
        Initialize all resources.
        """
        pass

    @abc.abstractmethod
    def finalize(self):
        """
        Finalize all resources.
        """
        pass

    def command(self, command_name: str, param: Dict, **kwargs) -> Dict:
        return {}


class BasicResourceManager(ResourceManager):
    def __init__(self, config: Dict):
        super(BasicResourceManager, self).__init__(config)
        self._resource_id_map: Dict[Union[uuid.UUID, str], Resource] = {}
        self._resource_name_map: Dict[str, Resource] = {}
        self._resource_type_map: Dict[str, List[Resource]] = {}
        if self.config.resources is not None:
            for resource_config in self.config.resources:
                resource: Resource = component.create_component(resource_config)
                self.add_resource(resource)
        if self.config.config.resources is not None:
            for resource_config in self.config.config.resources:
                resource: Resource = component.create_component(resource_config)
                self.add_resource(resource)

    def add_resource(self, resource: Resource):
        assert resource.id is not None
        if resource.id in self.resource_id_map:
            existed=self.resource_id_map[resource.id]
            raise ValueError(f'\
                Resource with id={resource.id} already existed.\
                \n    Existed: ({existed.group_id}, {existed.artifact_id}, {existed.version})\
                \n    Current: ({resource.group_id}, {resource.artifact_id}, {resource.version})\
                You can modify the id in the "config" field in the plugin config.yaml file\
            ')
        if resource.name in self.resource_name_map:
            existed=self.resource_name_map[resource.name]
            raise ValueError(f'\
                Resource with name={resource.name} already existed.\
                \n    Existed: ({existed.group_id}, {existed.artifact_id}, {existed.version})\
                \n    Current: ({resource.group_id}, {resource.artifact_id}, {resource.version})\
                You can modify the name in the "config" field in the plugin config.yaml file\
            ')
        self.resources.append(resource)
        self.resource_id_map[resource.id]=resource
        if resource.name is not None and len(resource.name)>0:
            self.resource_name_map[resource.name]=resource
        if resource.resource_type not in self.resource_type_map:
            self.resource_type_map[resource.resource_type]=[]
        self.resource_type_map[resource.resource_type].append(resource)

    def initialize(self):
        for resource in self.resource_id_map.values():
            resource.initialize()

    def finalize(self):
        for resource in self.resource_id_map.values():
            resource.finalize()
