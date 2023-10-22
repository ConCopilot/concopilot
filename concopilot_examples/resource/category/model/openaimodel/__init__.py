# -*- coding: utf-8 -*-

from typing import Dict

from .openaimodel import OpenAILLM


def constructor(config: Dict):
    return OpenAILLM(config)


__all__=[
    'constructor'
]
