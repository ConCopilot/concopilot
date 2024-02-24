# -*- coding: utf-8 -*-

import uuid

from typing import Union
from .. import ClassDict


class Identity(ClassDict):
    def __init__(self, *, role: str = None, id: Union[uuid.UUID, str, int] = None, name: str = None, **kwargs):
        super(Identity, self).__init__(**kwargs)
        if role is not None:
            self.role: str = role
        if id is not None:
            self.id: Union[uuid.UUID, str, int] = id
        if name is not None:
            self.name: str = name
