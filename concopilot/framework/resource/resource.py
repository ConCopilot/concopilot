# -*- coding: utf-8 -*-

import abc

from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .manager import ResourceManager

from ..plugin import AbstractPlugin


class Resource(AbstractPlugin):
    """
    A Resource is an infrastructure, hardware, software, or service that some plugins rely on.
    Such as a disk, a memory, a model, a DB connection, a service, or anything else that needs to be "initialized" before used by others,
    and/or needs to be "released" or "finalized" before the copilot exits.
    """

    def __init__(self, config: Dict):
        """
        Configure the Resource without initialization.

        Make sure the `type` in the config file is set to "resource".

        A `resource_type` field is need in the config file to indicate the type of the resource.

        :param config: configures read from its config file (default to "config.yaml")
        """
        super(Resource, self).__init__(config)
        assert self.type=='resource'
        self._resource_type=str(self.config.resource_type).lower()

    @property
    def resource_type(self) -> str:
        """
        :return: the resource type
        """
        return self._resource_type

    def config_resources(self, resource_manager: 'ResourceManager'):
        pass

    @abc.abstractmethod
    def initialize(self):
        """
        Initialize this resource basing on its `config` property.
        """
        pass

    @abc.abstractmethod
    def finalize(self):
        """
        Finalize/Release this resource.
        """
        pass

    def command(self, command_name: str, param: Dict, **kwargs) -> Dict:
        return {}
