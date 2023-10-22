# -*- coding: utf-8 -*-

from typing import Dict

from .translator import Translator


def constructor(config: Dict):
    return Translator(config)


__all__=[
    'constructor'
]
