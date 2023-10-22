# -*- coding: utf-8 -*-

from typing import Dict

from .duckduckgosearch import DuckDuckGoSearch


def constructor(config: Dict):
    return DuckDuckGoSearch(config)


__all__=[
    'constructor'
]
