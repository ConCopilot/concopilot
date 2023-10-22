# -*- coding: utf-8 -*-

from typing import Dict

from .openaicerebrum import OpenAICerebrum


def constructor(config: Dict):
    return OpenAICerebrum(config)


__all__=[
    'constructor'
]
