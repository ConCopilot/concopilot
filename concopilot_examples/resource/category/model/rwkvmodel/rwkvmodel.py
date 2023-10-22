# -*- coding: utf-8 -*-

import huggingface_hub
import validators
import requests
import os

from typing import Dict, List, Union

from rwkv.model import RWKV
from rwkv.utils import PIPELINE
from concopilot.framework.resource.category import LLM
from concopilot.package.config import Settings


settings=Settings()


class RWKVModel(LLM):
    def __init__(self, config):
        super(RWKVModel, self).__init__(config)
        self.repo_id: str = self.config.config.repo_id
        self.model_name: str = self.config.config.model_name
        self.cache_dir: str = self.config.config.cache_dir if os.path.isabs(self.config.config.cache_dir) else os.path.join(settings.working_directory, self.config.config.cache_dir)
        self.rwkv_strategy: str = self.config.config.rwkv_strategy
        self.tokenizer_file: str = self.config.config.tokenizer_file
        self.tokenizer_url: str = self.config.config.tokenizer_url
        self.tokenizer_force_update: bool = self.config.config.tokenizer_force_update
        self.pad_tokens: List[int] = self.config.config.pad_tokens

        self.model: RWKV = None
        self.pipeline: PIPELINE = None

    def inference(self, param: Union[LLM.LLMParameter, Dict], **kwargs) -> LLM.LLMResponse:
        if kwargs is not None:
            param=dict(param)
            param.update(kwargs)

        max_tokens=param['max_tokens'] if 'max_tokens' in param else self.config.config.max_tokens
        repetition_penalty=param['repetition_penalty'] if 'repetition_penalty' in param else self.config.config.repetition_penalty
        temperature=param['temperature'] if 'temperature' in param else self.config.config.temperature
        top_p=param['top_p'] if 'top_p' in param else self.config.config.top_p
        top_k=param['top_k'] if 'top_k' in param else self.config.config.top_k

        input_tokens=self.pad_tokens+self.pipeline.encode(param['prompt'])
        output_tokens=[]
        occurrence={}
        state=None
        token=None
        for i in range(max_tokens):
            tokens=input_tokens if i==0 else [token]

            logits, state=self.pipeline.model.forward(tokens, state)
            for n in occurrence:
                logits[n]-=(repetition_penalty+occurrence[n]*repetition_penalty)  # repetition penalty

            token=self.pipeline.sample_logits(logits, temperature=temperature, top_p=top_p, top_k=top_k)  # topp = 0 --> greedy decoding
            if token==0:
                break  # exit when 'endoftext'

            output_tokens+=[token]
            occurrence[token]=occurrence[token]+1 if token in occurrence else 1

        response=LLM.LLMResponse(
            content=self.pipeline.decode(output_tokens)
        )
        if param.get('require_token_len'):
            response.input_token_len=len(input_tokens)
            response.output_token_len=len(output_tokens)
        if param.get('require_cost'):
            response.cost=0
        return response

    def initialize(self):
        model_path=huggingface_hub.hf_hub_download(
            repo_id=self.repo_id,
            filename=self.model_name,
            cache_dir=self.cache_dir
        )

        tokenizer_file=self.config_file_path(self.tokenizer_file)
        if self.tokenizer_force_update or not os.path.isfile(tokenizer_file):
            if validators.url(self.tokenizer_url, simple_host=True):
                response=requests.get(self.tokenizer_url)
                if response.status_code==200:
                    with open(tokenizer_file, 'w') as file:
                        file.write(response.text)
                else:
                    raise requests.exceptions.RequestException(response.text)
            else:
                raise ValueError('No tokenizer_file found, and no valid tokenizer_url found.')

        self.model=RWKV(model=model_path, strategy=self.rwkv_strategy)
        self.pipeline=PIPELINE(self.model, tokenizer_file)

    def finalize(self):
        pass
