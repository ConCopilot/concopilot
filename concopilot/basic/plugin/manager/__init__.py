# -*- coding: utf-8 -*-

from typing import Dict

from concopilot.framework.plugin.manager import BasicPluginManager


def constructor(config: Dict):
    return BasicPluginManager(config)


__all__=[
    'constructor'
]
