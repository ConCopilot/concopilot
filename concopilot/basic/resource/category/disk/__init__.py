# -*- coding: utf-8 -*-

from typing import Dict

from concopilot.framework.resource.category import Disk


def constructor(config: Dict):
    return Disk(config)


__all__=[
    'constructor'
]
