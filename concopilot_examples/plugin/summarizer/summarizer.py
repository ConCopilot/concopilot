# -*- coding: utf-8 -*-

import json

from typing import Dict, List, Any

from concopilot.framework.plugin import AbstractPlugin
from concopilot.framework.resource.category import LLM
from concopilot.util import ClassDict
from concopilot.util.jsons import JsonEncoder


class Summarizer(AbstractPlugin):
    def __init__(self, config: Dict):
        super(Summarizer, self).__init__(config)
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

    def summarize(self, contents: List[Any], previous_summary: str = None) -> str:
        content='\n\n'.join([x if isinstance(x, str) else json.dumps(x, cls=JsonEncoder, ensure_ascii=False) for x in contents])
        response=self.model.inference(param={
            'prompt': self.instruction.replace('{content}', content).replace('{previous_summary}', previous_summary if previous_summary else '<No summary currently>').replace('{max_tokens}', str(self.max_tokens)),
            'max_tokens': self.max_tokens
        })
        return response['content']

    def command(self, command_name: str, param: Dict, **kwargs) -> Dict:
        if command_name=='summarize':
            return ClassDict(summary=self.summarize(
                param['contents'],
                param.get('previous_summary')
            ))
        else:
            raise ValueError(f'Unknown command: {command_name}. Only "summarize" is acceptable.')
