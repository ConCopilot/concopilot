# -*- coding: utf-8 -*-

from typing import Dict

from concopilot.framework.plugin import AbstractPlugin
from concopilot.framework.resource.category import LLM
from concopilot.util import ClassDict


class Translator(AbstractPlugin):
    def __init__(self, config: Dict):
        super(Translator, self).__init__(config)
        self._model: LLM = None
        self.max_tokens: int = self.config.config.max_tokens
        assert self.config.config.instruction_file
        with open(self.config_file_path(self.config.config.instruction_file)) as file:
            self.instruction: str = file.read()

    @property
    def model(self) -> LLM:
        if self._model is None:
            self._model=self.resources[0]
            assert isinstance(self._model, LLM)
        return self._model

    def translate(self, content: str, target_language: str) -> str:
        response=self.model.inference(param={
            'prompt': self.instruction.replace('{content}', content).replace('{target_language}', target_language).replace('{max_tokens}', str(self.max_tokens)),
            'max_tokens': self.max_tokens
        })
        return response['content']

    def command(self, command_name: str, param: Dict, **kwargs) -> Dict:
        if command_name=='translate':
            return ClassDict(content=self.translate(
                param['content'],
                param['target_language']
            ))
        else:
            raise ValueError(f'Unknown command: {command_name}. Only "translate" is acceptable.')
