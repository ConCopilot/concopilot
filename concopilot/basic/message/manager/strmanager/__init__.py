# -*- coding: utf-8 -*-

from typing import Dict

from .manager import BasicStrMessageManager


def constructor(config: Dict):
    return BasicStrMessageManager(config)


__all__=[
    'constructor'
]
