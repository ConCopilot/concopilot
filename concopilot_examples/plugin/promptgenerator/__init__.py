# -*- coding: utf-8 -*-

from typing import Dict

from .generator import LanguageModelPluginPromptGenerator


def constructor(config: Dict):
    return LanguageModelPluginPromptGenerator(config)


__all__=[
    'constructor'
]
