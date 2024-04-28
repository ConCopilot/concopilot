# -*- coding: utf-8 -*-

from typing import Dict

from ....framework.interface import BasicDuplexUserInterface


def constructor(config: Dict):
    return BasicDuplexUserInterface(config)


__all__=[
    'constructor'
]
