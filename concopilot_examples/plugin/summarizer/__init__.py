# -*- coding: utf-8 -*-

from typing import Dict

from .summarizer import Summarizer


def constructor(config: Dict):
    return Summarizer(config)


__all__=[
    'constructor'
]
