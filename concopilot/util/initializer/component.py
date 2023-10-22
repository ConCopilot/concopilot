# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import importlib

from typing import Callable, Dict, Tuple, List, Sequence, Any
from ..config.tool import get_config_folder, read_config_file
from ..class_dict import ClassDict
from ...package import repo
from ...package.config import Settings


settings=Settings()


def get_component_config_file_path(config: ClassDict) -> Tuple[str, str, str]:
    if config.config_folder is not None and config.config_folder.strip()!='':
        config_folder=config.config_folder
    else:
        config_folder=get_config_folder(os.path.join(settings.working_directory, '.runtime'), config.group_id, config.artifact_id, config.version, config.instance_id if config.instance_id is not None else '0')

    config_file, config_file_path=repo.retrieve_config(group_id=config.group_id, artifact_id=config.artifact_id, version=config.version, config_folder=config_folder, config_file=config.config_file, force_update=False)

    return config_folder, config_file, config_file_path


def get_component_constructor(config: ClassDict) -> Callable[[Dict, ...], Any]:
    if not settings.skip_build and config.setup is not None and isinstance(config.setup, ClassDict) and config.setup.pip is not None and isinstance(config.setup.pip, List):
        for package in config.setup.pip:
            if isinstance(package, str):
                package=[package]
            elif not isinstance(package, Sequence):
                raise ValueError('Unrecognized package: '+str(package))
            subprocess.check_call([sys.executable, '-m', 'pip', 'install']+package)
    return importlib.import_module(config.setup.package).constructor


def config_component_config_meta(component_config: ClassDict, config_folder: str, config_file: str, parent_config: ClassDict = None):
    assert component_config is not None
    assert config_folder is not None
    assert config_file is not None

    if component_config.config is None:
        component_config.config=ClassDict()
    if parent_config is not None and parent_config.config is not None:
        component_config.config.update(parent_config.config)
    component_config._config_info=ClassDict(
        config_folder=config_folder,
        config_file=config_file
    )
    return component_config


def construct_component(component_config, *args, **kwargs) -> Any:
    constructor=get_component_constructor(component_config)
    return constructor(component_config, *args, **kwargs)


def get_component_config(config: ClassDict) -> ClassDict:
    config_folder, config_file, config_file_path=get_component_config_file_path(config)
    component_config=read_config_file(config_file_path)
    component_config=config_component_config_meta(component_config, config_folder, config_file, parent_config=config)
    return component_config


def create_component(config: ClassDict, *args, **kwargs) -> Any:
    component_config=get_component_config(config)
    return construct_component(component_config, *args, **kwargs)


def create(config_folder: str = None, config_file: str = None, config_file_path: str = None, *args, **kwargs) -> Any:
    if config_folder is not None and config_file is not None:
        config_file_path=os.path.join(config_folder, config_file)
    elif config_file_path is not None:
        config_folder, config_file=os.path.split(config_file_path)
    else:
        raise ValueError('Either (config_folder, config_file) or config_file_path should exist.')
    component_config=read_config_file(config_file_path)
    component_config=config_component_config_meta(component_config, config_folder, config_file, parent_config=None)
    return construct_component(component_config, *args, **kwargs)
