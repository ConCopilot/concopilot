# -*- coding: utf-8 -*-

import os
import yaml

from ..class_dict import ClassDict


def get_config_folder(root: str, group_id: str, artifact_id: str, version: str, instance_id=None) -> str:
    assert root is not None and len(root)>0
    assert group_id is not None and len(group_id)>0
    assert artifact_id is not None and len(artifact_id)>0
    assert version is not None and len(version)>0
    dir_list=[root]+group_id.split('.')+[artifact_id, version]
    if instance_id is not None:
        dir_list.append(instance_id)
    return os.path.join(*dir_list)


def read_config_file(config_file_path) -> ClassDict:
    with open(config_file_path, 'r', encoding='utf8') as file:
        return ClassDict.convert(yaml.safe_load(file))
