# -*- coding: utf-8 -*-


class ConCopilotError(Exception):
    def __init__(self, msg: str):
        self.msg=msg
