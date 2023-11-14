# -*- coding: utf-8 -*-

from typing import Dict

from .interactor import AutoInteractor


def constructor(config: Dict, *args):
    return AutoInteractor(config, *args)


__all__=[
    'constructor'
]
