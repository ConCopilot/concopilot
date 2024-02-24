# -*- coding: utf-8 -*-

import json
import uuid
import numpy as np


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, set):
            return self.default(list(obj))
        return json.JSONEncoder.default(self, obj)
