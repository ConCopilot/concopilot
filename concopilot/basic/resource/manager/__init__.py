# -*- coding: utf-8 -*-

from typing import Dict

from ....framework.resource import BasicResourceManager


def constructor(config: Dict):
    return BasicResourceManager(config)


__all__=[
    'constructor'
]
