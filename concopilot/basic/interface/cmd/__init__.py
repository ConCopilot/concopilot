# -*- coding: utf-8 -*-

from typing import Dict

from .interface import CmdUserInterface


def constructor(config: Dict):
    return CmdUserInterface(config)


__all__=[
    'constructor'
]
