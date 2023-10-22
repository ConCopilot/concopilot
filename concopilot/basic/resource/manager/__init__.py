# -*- coding: utf-8 -*-

from typing import Dict

from concopilot.framework.resource import BasicResourceManager


def constructor(config: Dict):
    return BasicResourceManager(config)


__all__=[
    'constructor'
]
