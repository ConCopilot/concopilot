# -*- coding: utf-8 -*-

from typing import Dict

from .rwkvcerebrum import RWKVCerebrum


def constructor(config: Dict):
    return RWKVCerebrum(config)


__all__=[
    'constructor'
]
