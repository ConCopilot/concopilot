# -*- coding: utf-8 -*-

from typing import Dict

from .manager import BasicJsonMessageManager


def constructor(config: Dict):
    return BasicJsonMessageManager(config)


__all__=[
    'constructor'
]
