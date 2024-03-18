# -*- coding: utf-8 -*-

import argparse
import os
import sys

from typing import Tuple, List, Generator

from requests import Session
from concopilot.package import config
from concopilot.package import validator
from concopilot.package import repo
from concopilot.framework import run
from concopilot.util import ClassDict


def get_args(args=None) -> Tuple[ClassDict, List[str]]:
    parser=argparse.ArgumentParser()
    parser.add_argument('--settings', type=str, default=None)
    parser.add_argument('--working-directory', type=str, default=None)
    parser.add_argument('--skip-setup', action='store_true', default=False)
    parser.add_argument('--pip-params', type=str, default=None)

    parser.add_argument('--repo-user-name', type=str, default=None)
    parser.add_argument('--repo-user-pwd', type=str, default=None)
    parser.add_argument('--gpg-passphrase', type=str, default=None)
    parser.add_argument('--gnupg-home', type=str, default=None)
    parser.add_argument('--recursive', action='store_true', default=False)

    parser.add_argument('--src-folder', type=str, default=None)

    parser.add_argument('--add-current-folder-to-path', action='store_true', default=None)
    parser.add_argument('--add-working-directory-to-path', action='store_true', default=None)
    parser.add_argument('--add-src-folder-to-path', action='store_true', default=None)

    parser.add_argument('--help-cmd', action='store_true', default=None)
    param, argv=parser.parse_known_args(args)
    param=ClassDict(**param.__dict__)
    return param, argv


def install(config_folder, config_file):
    group_id, artifact_id, version=validator.validate_component_config_file(config_file)
    repo.to_local_repo(group_id, artifact_id, version, config_folder=config_folder)
    return group_id, artifact_id, version


def get_config_folder(path: str):
    return os.path.join(path, config.default_config_folder)


def valid_config_folders(root_dir: str, level: int = -1) -> Generator[str, None, None]:
    config_folder=get_config_folder(root_dir)
    if os.path.isdir(config_folder):
        yield config_folder
    elif level!=0:
        for name in os.listdir(root_dir):
            path=os.path.join(root_dir, name)
            if name!='__pycache__' and os.path.isdir(path):
                yield from valid_config_folders(path, level-1)


def get_valid_config_folders(root_dir: str, recursive: bool = False):
    yield from valid_config_folders(root_dir, level=-1 if recursive else 0)


def get_valid_configs(src_folder: str, recursive: bool = False) -> Generator[Tuple[str, str], None, None]:
    for src_config_folder in get_valid_config_folders('.' if (src_folder is None or src_folder.strip()=='') else src_folder, recursive):
        for name in config.default_config_files:
            src_config_file=os.path.join(src_config_folder, name)
            if os.path.isfile(src_config_file):
                yield src_config_folder, src_config_file


def get_help_str(command: str = None) -> str:
    if command=='build':
        return ('usage: conpack build\n'
                '               [--settings=<settings>] # The `conpack` config setting file path, absent for default\n'
                '               [--working-directory=<working_directory>] # The working directory (where to place the ".runtime" folder), default to current directory\n'
                '               [\n'
                '                   [--group-id=<group-id> --artifact-id=<artifact-id> --version=<version>]\n'
                '                   [--src-folder=<src_folder>] # The source folder (where the ".config" folder exists), default to current directory\n'
                '                   [--config-file=<config-file>] # The config.yaml file path\n'
                '               ]\n'
                '               [--skip-setup]\n'
                '               [--pip-params=<pip_params>] # Additional parameters to be passed to pip when installing a python package\n'
                '               [--add-current-folder-to-path] # Whether add the current folder to path\n'
                '               [--add-working-directory-to-path] # Whether add the working directory to path\n'
                '               [--add-src-folder-to-path] # Whether add the source folder to path\n'
                '               [*argv]')
    elif command=='run':
        return ('usage: conpack run\n'
                '               [--settings=<settings>] # The `conpack` config setting file path, absent for default\n'
                '               [--working-directory=<working_directory>] # The working directory (where to place the ".runtime" folder), default to current directory\n'
                '               [\n'
                '                   [--group-id=<group-id> --artifact-id=<artifact-id> --version=<version>]\n'
                '                   [--src-folder=<src_folder>] # The source folder (where the ".config" folder exists), default to current directory\n'
                '                   [--config-file=<config-file>] # The config.yaml file path\n'
                '               ]\n'
                '               [--skip-setup]\n'
                '               [--pip-params=<pip_params>] # Additional parameters to be passed to pip when installing a python package\n'
                '               [--add-current-folder-to-path] # Whether add the current folder to path\n'
                '               [--add-working-directory-to-path] # Whether add the working directory to path\n'
                '               [--add-src-folder-to-path] # Whether add the source folder to path\n'
                '               [*argv]')
    elif command=='install':
        return ('usage: conpack install\n'
                '               [--settings=<settings>] # The `conpack` config setting file path, absent for default\n'
                '               [--working-directory=<working_directory>] # The working directory (where to place the ".runtime" folder), default to current directory\n'
                '               [--src-folder=<src_folder>] # The source folder (where the ".config" folder exists), default to current directory\n'
                '               [--skip-setup]\n'
                '               [--pip-params=<pip_params>] # Additional parameters to be passed to pip when installing a python package\n'
                '               [--recursive] # check all sub-folder of the <src_folder> for possible config files\n'
                '               [--add-current-folder-to-path] # Whether add the current folder to path\n'
                '               [--add-working-directory-to-path] # Whether add the working directory to path\n'
                '               [--add-src-folder-to-path] # Whether add the source folder to path\n'
                '               [*argv]')
    elif command=='deploy':
        return ('usage: conpack deploy\n'
                '               [--settings=<settings>] # The `conpack` config setting file path, absent for default\n'
                '               [--working-directory=<working_directory>] # The working directory (where to place the ".runtime" folder), default to current directory\n'
                '               [--src-folder=<src_folder>] # The source folder (where the ".config" folder exists), default to current directory\n'
                '               [--skip-setup]\n'
                '               [--pip-params=<pip_params>] # Additional parameters to be passed to pip when installing a python package\n'
                '               [--recursive] # check all sub-folder of the <src_folder> for possible config files\n'
                '               [--repo-user-name=<repo_user_name>] [--repo-user-pwd=<repo_user_pwd>] [--gpg-passphrase=<gpg_passphrase>] [--gnupg-home=<gnupg_home>]\n'
                '               [--add-current-folder-to-path] # Whether add the current folder to path\n'
                '               [--add-working-directory-to-path] # Whether add the working directory to path\n'
                '               [--add-src-folder-to-path] # Whether add the source folder to path\n'
                '               [*argv]')
    else:
        return ('usage: conpack <build|run|install|deploy>\n'
                '               [--settings=<settings>] [--working-directory=<working_directory>] [--skip-setup] [--pip-params=<pip_params>] [--recursive]\n'
                '               [--repo-user-name=<repo_user_name>] [--repo-user-pwd=<repo_user_pwd>] [--gpg-passphrase=<gpg_passphrase>] [--gnupg-home=<gnupg_home>]\n'
                '               [--src-folder=<src_folder>]\n'
                '               [--add-current-folder-to-path] [--add-working-directory-to-path] [--add-src-folder-to-path]\n'
                '               [*argv]')


def execute(*args, **kwargs):
    import logging
    logging.basicConfig(level=logging.INFO)
    logger=logging.getLogger('[ConCopilot]')

    param, argv=get_args(args if args else None)
    param.update({k: v for k, v in kwargs.items() if k in param})
    if not param.src_folder:
        param.src_folder='.'
    settings=config.load_settings(settings_path=param.settings, working_directory=param.working_directory, skip_setup=param.skip_setup, pip_params=param.pip_params)

    if param.add_current_folder_to_path:
        abs_path=str(os.path.abspath('.'))
        if abs_path not in sys.path:
            sys.path.append(abs_path)
    if param.add_working_directory_to_path and settings.working_directory:
        abs_path=str(os.path.abspath(settings.working_directory))
        if abs_path not in sys.path:
            sys.path.append(abs_path)
    if param.add_src_folder_to_path and param.src_folder:
        abs_path=str(os.path.abspath(param.src_folder))
        if abs_path not in sys.path:
            sys.path.append(abs_path)

    if len(argv)>0:
        command=argv[0].strip().lower()
        argv=argv[1:]
    else:
        command=None
    folder_count=0
    plugin=None
    plugin_list=None
    if command is None or command=='help' or param.help_cmd:
        print(get_help_str(command))
        folder_count=-1
    elif command=='build':
        # copy component config files into ./.runtime
        # check and install component dependencies
        run_param, run_argv=run.get_args(argv)
        run_param.update({k: v for k, v in kwargs.items() if k in run_param})
        if len(run_param)>0:
            logger.info(f'---------------- building ----------------')
            plugin=run.build(run_param, *run_argv)
            folder_count+=1
        else:
            plugin_list=[]
            for src_config_folder, src_config_file in get_valid_configs(param.src_folder, param.recursive):
                logger.info(f'---------------- building {src_config_folder} ----------------')
                if os.path.isfile(src_config_file):
                    plugin_list.append([src_config_file, run.build(ClassDict(config_file=src_config_file), argv[2:])])
                    folder_count+=1
    elif command=='run':
        # do build, and run copilot
        run_param, run_argv=run.get_args(argv)
        run_param.update({k: v for k, v in kwargs.items() if k in run_param})
        if len(run_param)>0:
            logger.info(f'---------------- running ----------------')
            run.run(run_param, *run_argv)
            folder_count+=1
        else:
            for src_config_folder, src_config_file in get_valid_configs(param.src_folder, param.recursive):
                logger.info(f'---------------- running {src_config_folder} ----------------')
                run.run(ClassDict(config_file=src_config_file), argv[2:])
                folder_count+=1
    elif command=='install':
        # check if source folder is a component definition
        # copy config files from ./.config into local repo
        for src_config_folder, src_config_file in get_valid_configs(param.src_folder, param.recursive):
            if not param.skip_setup and os.path.isfile(src_config_file):
                logger.info(f'---------------- building {src_config_folder} ----------------')
                run.build(ClassDict(config_file=src_config_file), argv[2:])
            logger.info(f'---------------- installing {src_config_folder} ----------------')
            install(src_config_folder, src_config_file)
            logger.info(f'{src_config_folder} successfully installed into local repository.\n')
            folder_count+=1
    elif command=='deploy':
        # do install, and push the component definition to remote repo
        with Session() as session:
            for src_config_folder, src_config_file in get_valid_configs(param.src_folder, param.recursive):
                if not param.skip_setup and os.path.isfile(src_config_file):
                    logger.info(f'---------------- building {src_config_folder} ----------------')
                    run.build(ClassDict(config_file=src_config_file), argv[2:])
                logger.info(f'---------------- deploying {src_config_folder} ----------------')
                group_id, artifact_id, version=install(src_config_folder, src_config_file)
                repo.to_remote_repo(session, group_id, artifact_id, version, name=param.repo_user_name, pwd=param.repo_user_pwd, gpg=True, gpg_passphrase=param.gpg_passphrase, gnupghome=param.gnupg_home)
                folder_count+=1
    else:
        logger.error(f'Unknown command {command}.\n'+get_help_str(command))

    if folder_count==0:
        logger.warning('No valid source folder detected. Nothing has been done.\n'
                       f'  A valid source folder must contains a `{config.default_config_folder}` folder with a {config.default_config_files[0]} file in it.')

    if plugin is not None:
        return plugin
    elif plugin_list is not None:
        if param.recursive:
            return plugin_list
        elif len(plugin_list)>0:
            return plugin_list[0]
        else:
            return None
    else:
        return None


if __name__=='__main__':
    execute()
