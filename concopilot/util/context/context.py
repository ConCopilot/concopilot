# -*- coding: utf-8 -*-

import uuid

from typing import Dict, Union, Mapping, Any

from ..class_dict import ClassDict
from ...framework.storage import Storage
from ...framework.interface import UserInterface


class Asset(ClassDict):
    def __init__(self, *, type: str, id: Union[uuid.UUID, str] = None, name: str = None, description: str = None, content: str = None, data: Any = None, **kwargs):
        super(Asset, self).__init__(**kwargs)
        self.type: str = type
        self.id: Union[uuid.UUID, str] = id
        self.name: str = name
        self.description: str = description
        self.content: str = content
        self.data: Any = data

    @staticmethod
    def convert_assets(assets: Dict[str, 'Asset']):
        if not isinstance(assets, ClassDict):
            assets=ClassDict(**assets)
        update={}
        for k, v in assets.items():
            if not isinstance(v, Mapping):
                raise ValueError(f'assets contains non-mapping objects!')
            if not isinstance(v, Asset):
                update[k]=Asset(**ClassDict.convert(v))
        assets.update(update)
        return assets


class Context(ClassDict):
    def __init__(self, *, storage: Storage = None, assets: Dict[str, Asset] = None, user_interface: UserInterface = None, **kwargs):
        super(Context, self).__init__(**kwargs)
        self.storage: Storage = storage
        self.assets: ClassDict[str, Asset] = ClassDict.convert(assets)
        self.user_interface: UserInterface = user_interface
