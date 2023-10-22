# -*- coding: utf-8 -*-

import json
import uuid


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, set):
            return self.default(list(obj))
        return json.JSONEncoder.default(self, obj)
