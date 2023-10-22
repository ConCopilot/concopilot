# -*- coding: utf-8 -*-

from typing import Dict

from .storage import DiskStorage


def constructor(config: Dict):
    return DiskStorage(config)


__all__=[
    'constructor'
]
