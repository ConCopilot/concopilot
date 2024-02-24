# -*- coding: utf-8 -*-

import os
import pathlib
import copy
import pickle

from typing import Dict, Any

from ....framework.storage import Storage
from ....framework.resource import ResourceManager
from ....framework.resource.category import Disk
from ....util.context import Asset
from ....util import ClassDict
from ....package.config import Settings


settings=Settings()


class DiskStorage(Storage):
    def __init__(self, config: Dict):
        super(DiskStorage, self).__init__(config)
        self.root: str = os.path.abspath(self.config.config.root_directory if self.config.config.root_directory else (settings.working_directory if settings.working_directory else '.'))
        self.sub_root: str = os.path.join(self.root, self.config.config.sub_root_key)
        self.asset_key: str = self.config.config.asset_key
        self.disk: Disk = None
        self._sub={}

    def config_resources(self, resource_manager: ResourceManager):
        super(DiskStorage, self).config_resources(resource_manager)
        self.disk=self.resources[0]
        assert isinstance(self.disk, Disk)
        if not pathlib.Path(self.root).is_relative_to(self.disk.root):
            raise ValueError(f'The configure Storage path ({self.root}) is not under the configured Resource Disk path ({str(self.disk.root)})')

    def _path(self, key: str) -> str:
        path=os.path.join(self.root, key)
        if path.startswith(self.sub_root):
            raise ValueError(f'Destination should not in {self.sub_root}.')
        return path

    def _sub_path(self, key: str) -> str:
        return os.path.join(self.sub_root, key)

    def get(self, key: str) -> Any:
        key=key.strip()
        if not key:
            raise ValueError('key must be a valid string')
        try:
            info=self.disk.read_file(self._path(key+'.info'), binary=False)
            value=self.disk.read_file(self._path(key), binary=info!='text')
            if info=='pickle':
                value=pickle.loads(value)
            return value
        except FileNotFoundError:
            return None

    def put(self, key: str, value: Any):
        key=key.strip()
        if not key:
            raise ValueError('key must be a valid string')
        if isinstance(value, str):
            info='text'
        elif isinstance(value, bytes):
            info='binary'
        else:
            value=pickle.dumps(value)
            info='pickle'
        self.disk.write_file(self._path(key), value)
        self.disk.write_file(self._path(key+'.info'), info)

    def remove(self, key: str) -> Any:
        key=key.strip()
        if not key:
            raise ValueError('key must be a valid string')
        try:
            content=self.get(key)
            path=self._path(key)
            self.disk.delete_file(path)
            self.disk.delete_file(path+'.info')
            path=os.path.split(path)[0]
            try:
                while path!=self.root and len([x for x in os.listdir(path)])==0:
                    self.disk.delete_folder(path)
                    path=os.path.split(path)[0]
            except ValueError:
                pass
            return content
        except FileNotFoundError:
            return None

    def get_sub_storage(self, key: str) -> Storage:
        key=key.strip()
        if not key:
            raise ValueError('key must be a valid string')
        if key not in self._sub:
            config=copy.deepcopy(self.config)
            config.root_directory=self._sub_path(key)
            self._sub[key]=DiskStorage(config)
        return self._sub[key]

    def remove_sub_storage(self, key: str) -> bool:
        key=key.strip()
        if not key:
            raise ValueError('key must be a valid string')
        if key in self._sub:
            path=self._sub_path(key)
            self.disk.delete_folder(path)
            self._sub.pop(key)
            return True
        return False

    def command(self, command_name: str, param: Any, **kwargs) -> Any:
        file_path=param['file_path']
        if os.path.isabs(file_path):
            raise ValueError('Only relative file paths are acceptable.')
        if '.' in os.path.splitext(file_path)[0]:
            raise ValueError("'.' is not allowed in file_path unless it is the filename extension separator.")
        if command_name=='read':
            return ClassDict(content=self.get(file_path))
        elif command_name=='write':
            self.put(file_path, param['content'])
            if self.asset_key:
                if self.asset_key not in self.context.assets:
                    self.context.assets[self.asset_key]=Asset(
                        asset_type='storage location',
                        content_type="<class 'list'>",
                        content=[]
                    )
                self.context.assets[self.asset_key].content.append(file_path)
                self.context.assets[self.asset_key].content=list(set(self.context.assets[self.asset_key].content))
            return ClassDict(status=True)
        elif command_name=='delete':
            self.remove(file_path)
            if self.asset_key and self.asset_key in self.context.assets:
                if file_path in self.context.assets[self.asset_key].content:
                    self.context.assets[self.asset_key].content.remove(file_path)
                if len(self.context.assets[self.asset_key].content)==0:
                    self.context.assets.pop(self.asset_key)
            return ClassDict(status=True)
        else:
            raise ValueError(f'Unknown command: {command_name}. Only "read", "write", and "delete" are acceptable.')
