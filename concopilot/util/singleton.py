# -*- coding: utf-8 -*-

import abc


class SingletonMeta(abc.ABCMeta, type):
    _instances={}

    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self]=super(SingletonMeta, self).__call__(*args, **kwargs)
        return self._instances[self]


class Singleton(abc.ABC, metaclass=SingletonMeta):
    pass
