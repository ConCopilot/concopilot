# -*- coding: utf-8 -*-

from typing import Dict

from concopilot.framework import BasicCopilot


def constructor(config: Dict):
    return BasicCopilot(config)


__all__=[
    'constructor'
]
