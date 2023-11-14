# -*- coding: utf-8 -*-

from typing import Dict

from .interactor import ChatInteractor


def constructor(config: Dict, *args):
    return ChatInteractor(config, *args)


__all__=[
    'constructor'
]
