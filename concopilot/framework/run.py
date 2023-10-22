# -*- coding: utf-8 -*-

import argparse
import requests

from typing import Tuple, List

from .plugin import Plugin
from .copilot import Copilot
from ..util.initializer import component
from ..util import ClassDict
from ..package.config import Settings


settings=Settings()


def get_args(args=None) -> Tuple[ClassDict, List[str]]:
    parser=argparse.ArgumentParser()
    parser.add_argument('--group-id', type=str, default=None)
    parser.add_argument('--artifact-id', type=str, default=None)
    parser.add_argument('--version', type=str, default=None)
    parser.add_argument('--config-file', type=str, default=None)
    param, argv=parser.parse_known_args(args)
    param=ClassDict(**param.__dict__)
    return param, argv


def build(param: ClassDict, *args, **kwargs) -> Plugin:
    # TODO: make a docker isolated env for safety issue
    if param.group_id and param.artifact_id and param.version:
        with requests.Session() as s:
            settings.network_session=s
            plugin: Plugin = component.create_component(param, *args, **kwargs)
            settings.network_session=None
    elif param.config_file:
        with requests.Session() as s:
            settings.network_session=s
            plugin: Plugin = component.create(config_file_path=param.config_file, *args, **kwargs)
            settings.network_session=None
    else:
        raise ValueError('Either a ("group-id", "artifact-id", "version") combination or a config file path should be provided.\n'
                         'run with:\n'
                         '          --group-id=<group_id> --artifact-id=<artifact_id> --version=<version> *argv\n'
                         '      or\n'
                         '          --config-file=<config_file> *argv')
    return plugin


def run(param: ClassDict, *args, **kwargs):
    plugin: Plugin = build(param, *args, **kwargs)
    if isinstance(plugin, Copilot):
        plugin.run()
    else:
        raise ValueError('The specific component is not a Copilot object, and cannot be run.')


if __name__=='__main__':
    param, argv=get_args()
    run(param, *argv)
