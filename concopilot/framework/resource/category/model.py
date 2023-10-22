# -*- coding: utf-8 -*-

import abc

from typing import Dict, Union

from ...resource import Resource
from ....util import ClassDict


class Model(Resource):
    def __init__(self, config):
        super(Model, self).__init__(config)
        assert self.resource_type=='model'

    @abc.abstractmethod
    def inference(self, param: Dict, **kwargs) -> Dict:
        pass


class LLM(Model):
    class LLMParameter(ClassDict):
        def __init__(self,
                prompt: str = None, max_tokens: int = None, temperature: float = None,
                require_token_len: bool = None, require_cost: bool = None,
                **kwargs):
            super(LLM.LLMParameter, self).__init__(**kwargs)
            self.prompt: str = prompt
            self.max_tokens: int = max_tokens
            self.temperature: float = temperature

            self.require_token_len: bool = require_token_len
            self.require_cost: bool = require_cost

    class LLMResponse(ClassDict):
        def __init__(self, content: str, input_token_len: int = None, output_token_len: int = None, cost: float = None, **kwargs):
            super(LLM.LLMResponse, self).__init__(**kwargs)
            self.content: str = content

            self.input_token_len: int = input_token_len
            self.output_token_len: int = output_token_len
            self.cost: float = cost

    @abc.abstractmethod
    def inference(self, param: Union[LLMParameter, Dict], **kwargs) -> LLMResponse:
        pass
