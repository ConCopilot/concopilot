# -*- coding: utf-8 -*-

import copy

from typing import Sequence, Mapping, Any

from . import dicts


class ClassDict(dict):
    def __init__(self, **kwargs):
        super(ClassDict, self).__init__()
        if len(kwargs)>0:
            self.update(**ClassDict.convert(kwargs))

    def __getattr__(self, item):
        return self.get(item)

    def __setattr__(self, key, value):
        self[key]=value

    def __delattr__(self, item):
        del self[item]

    def __setitem__(self, key, value):
        assert isinstance(key, str), 'key must be str'
        super(ClassDict, self).__setitem__(key, value)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __copy__(self):
        cls=self.__class__
        result=cls.__new__(cls)
        result.update(self)
        return result

    def __deepcopy__(self, memodict={}):
        cls=self.__class__
        result=cls.__new__(cls)
        memodict[id(self)]=result
        for k, v in self.items():
            setattr(result, copy.deepcopy(k, memodict), copy.deepcopy(v, memodict))
        return result

    def hasattr(self, item):
        return item in self

    def update_nested(self, other: Mapping) -> None:
        for k, v in other.items():
            if isinstance(v, Mapping):
                map=self.get(k)
                if isinstance(map, Mapping):
                    if not isinstance(map, ClassDict):
                        map=ClassDict.convert(map)
                    map.update_nested(v)
                    self[k]=map
                else:
                    self[k]=ClassDict.convert(v)
            else:
                self[k]=v

    def flatten(self, parent_key: str = '', sep: str = '.', keep_none: bool = False, keep_container_type: bool = False) -> dict[str, Any]:
        return dicts.flatten_dict(self, parent_key=parent_key, sep=sep, keep_none=keep_none, keep_container_type=keep_container_type)

    @staticmethod
    def convert(obj: Any) -> Any:
        if isinstance(obj, Mapping):
            _obj=obj if isinstance(obj, ClassDict) else ClassDict()
            items=[x for x in obj.items()] if isinstance(obj, ClassDict) else obj.items()
            for k, v in items:
                _obj[k]=ClassDict.convert(v)
            return _obj
        elif isinstance(obj, Sequence) and not isinstance(obj, str) and not isinstance(obj, bytes):
            return [ClassDict.convert(x) for x in obj]
        elif isinstance(obj, set):
            return {ClassDict.convert(x) for x in obj}
        else:
            return obj
