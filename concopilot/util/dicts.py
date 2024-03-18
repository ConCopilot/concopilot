# -*- coding: utf-8 -*-

from typing import Mapping, List, Tuple, Any


def _flatten_dict_gen(d: Mapping, parent_key: str = '', sep: str = '.', keep_none: bool = False, keep_container_type: bool = False):
    for k, v in d.items():
        new_key=parent_key+sep+str(k) if parent_key else k
        if isinstance(v, Mapping):
            if keep_container_type:
                yield new_key, str(type(v))
            yield from _flatten_dict_gen(v, parent_key=new_key, sep=sep, keep_none=keep_none, keep_container_type=keep_container_type)
        elif isinstance(v, (List, Tuple)):
            if keep_container_type:
                yield new_key, str(type(v))
            yield from _flatten_dict_gen({str(i): x for i, x in enumerate(v)}, parent_key=new_key, sep=sep, keep_none=keep_none, keep_container_type=keep_container_type)
        else:
            if keep_none or v is not None:
                yield new_key, v


def flatten_dict(d: Mapping, parent_key: str = '', sep: str = '.', keep_none: bool = False, keep_container_type: bool = False) -> dict[str, Any]:
    return dict(_flatten_dict_gen(d, parent_key=parent_key, sep=sep, keep_none=keep_none, keep_container_type=keep_container_type))
