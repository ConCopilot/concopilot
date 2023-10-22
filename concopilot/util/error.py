# -*- coding: utf-8 -*-


class ConcopilotError(Exception):
    def __init__(self, msg: str):
        self.msg=msg
