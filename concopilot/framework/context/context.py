# -*- coding: utf-8 -*-

from typing import Dict

from ..asset import Asset
from ..interface import UserInterface
from ..storage import Storage
from ...util import ClassDict


class Context(ClassDict):
    def __init__(self, *, storage: Storage = None, assets: Dict[str, Asset] = None, user_interface: UserInterface = None, **kwargs):
        super(Context, self).__init__(**kwargs)
        self.storage: Storage = storage
        self.assets: ClassDict[str, Asset] = Asset.convert_assets(assets)
        self.user_interface: UserInterface = user_interface
