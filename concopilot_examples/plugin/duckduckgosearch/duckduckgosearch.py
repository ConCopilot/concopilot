# -*- coding: utf-8 -*-

import duckduckgo_search
import json

from typing import Dict, List

from itertools import islice
from concopilot.framework.plugin import AbstractPlugin
from concopilot.util import ClassDict


class DuckDuckGoSearch(AbstractPlugin):
    def __init__(self, config: Dict):
        super(DuckDuckGoSearch, self).__init__(config)
        self.num_results: int = self.config.config.num_results

    def search(self, query: str, num_results: int = None) -> List:
        if query:
            results=duckduckgo_search.DDGS().text(query)
            search_results=[item for item in islice(results, num_results if (num_results is not None and num_results>0) else self.num_results)]
        else:
            search_results=[]

        return json.loads(json.dumps(search_results, ensure_ascii=False).encode('utf-8', 'ignore').decode('utf-8'))

    def command(self, command_name: str, param: Dict, **kwargs) -> Dict:
        if command_name=='search':
            return ClassDict(results=self.search(param['query'], param.get('num_results')))
        else:
            raise ValueError(f'Unknown command: {command_name}. Only "search" is acceptable.')
