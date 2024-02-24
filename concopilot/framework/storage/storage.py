# -*- coding: utf-8 -*-

import abc

from typing import Dict, Any

from ..plugin import AbstractPlugin


class Storage(AbstractPlugin):
    """
    Store the long term memory of a copilot,
    as well as other kind of materials for a specific working flow,
    e.g., copilot assets.

    A storage can back on any kind of storage system resources, depending on the specific implementation,
    like hard disk, memory, redis, etc.
    """

    def __init__(self, config: Dict):
        """
        Configure the Storage without initialization.

        Make sure the `type` in the config file is set to "storage".

        :param config: configures read from its config file (default to "config.yaml")
        """
        super(Storage, self).__init__(config)
        assert self.type=='storage'

    @abc.abstractmethod
    def get(self, key: str) -> Any:
        """
        Get the stored object by the give `key`.

        :param key: the key related to the stored object
        :return: the stored object relating to the key, or None if not found
        """
        pass

    def get_or_default(self, key: str, default: Any) -> Any:
        """
        Get the stored object by the give `key`, or the `default` if not found.

        :param key: the key related to the stored object
        :param default: the default value if not found
        :return: the stored object relating to the key, or the given default value if not found
        """
        value=self.get(key)
        return value if value is not None else default

    @abc.abstractmethod
    def put(self, key: str, value: Any):
        """
        Put the `value` to the storage, relate it with the given `key`.

        :param key: the key related to the object
        :param value: the object to be stored
        """
        pass

    @abc.abstractmethod
    def remove(self, key: str) -> Any:
        """
        Remove the stored object related to the given `key`.

        :param key: the key related to the object
        :return: the stored object relating to the key, or None if not found
        """
        pass

    @abc.abstractmethod
    def get_sub_storage(self, key: str) -> 'Storage':
        """
        Return a sub-storage space of this storage.

        A sub-storage is a dedicated area in this storage for special use.

        Developers must make sure that:
        1. a sub-storage must be a subset of this parent storage,
        2. a sub-storage cannot access data in other part of the parent storage,
        3. it is recommended that the parent storage should not access data in even its own sub-storage.

        :param key: the key related to the sub-storage
        :return: the sub-storage relating to the key
        """
        pass

    @abc.abstractmethod
    def remove_sub_storage(self, key: str) -> bool:
        """
        Remove a sub-storage relating to the specified `key`.

        :param key: the key related to the sub-storage
        :return: True if success, and False if failed
        """
        pass

    def command(self, command_name: str, param: Any, **kwargs) -> Any:
        return {}
