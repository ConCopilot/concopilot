# -*- coding: utf-8 -*-

from typing import Dict

from .rwkvmodel import RWKVModel


def constructor(config: Dict):
    return RWKVModel(config)


__all__=[
    'constructor'
]
