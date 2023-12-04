# -*- coding: utf-8 -*-

import os
import pathlib
import shutil
import logging

from typing import Tuple

from requests import Session
from . import check
from . import transfer
from .config import Env, Settings, default_config_files, component_completion_flag
from .error import PackageException, PackageHttpException
from ..util.config.tool import get_config_folder
from ..util.config import versions


logger=logging.getLogger('[Concopilot]')


env=Env()
settings=Settings()


ignore_suffixes={'.md5', '.sha1', '.sha256', '.sha512', '.asc'}


def _ignore(dir, names):
    return [name for name in names if (pathlib.Path(name).suffix.lower() in ignore_suffixes or name==component_completion_flag)]


def check_config_file_existence(config_folder: str, config_file: str = None, artifact_id: str = None, version: str = None, check_completion: bool = False) -> Tuple[bool, str, str]:
    for config_file in (default_config_files if config_file is None else [config_file]):
        if artifact_id is not None and version is not None:
            config_file=to_repo_file_name(config_file, artifact_id, version)
        config_file_path=os.path.join(config_folder, config_file)
        if os.path.isfile(config_file_path):
            return True and (not check_completion or pathlib.Path(config_folder).joinpath(component_completion_flag).exists()), config_file, config_file_path
    return False, config_file, config_file_path


def from_repo_file_name(repo_file_name: str, artifact_id, version):
    return repo_file_name[len(artifact_id)+len(version)+2:] if repo_file_name.startswith('-'.join([artifact_id, version, ''])) else repo_file_name


def to_repo_file_name(original_file_name: str, artifact_id, version):
    return '-'.join([artifact_id, version, original_file_name])


def get_copy_from_repo_fn(artifact_id, version):
    def copy_to_repo_fn(src, dst, *args, follow_symlinks=True):
        dst=pathlib.Path(dst)
        dst=str(dst.parent.joinpath(from_repo_file_name(dst.name, artifact_id, version)))
        return shutil.copy2(src, dst, *args, follow_symlinks=follow_symlinks)
    return copy_to_repo_fn


def get_copy_to_repo_fn(artifact_id, version):
    def copy_to_repo_fn(src, dst, *args, follow_symlinks=True):
        dst=pathlib.Path(dst)
        dst=str(dst.parent.joinpath(to_repo_file_name(dst.name, artifact_id, version)))
        return shutil.copy2(src, dst, *args, follow_symlinks=follow_symlinks)
    return copy_to_repo_fn


def from_local_repo(group_id: str, artifact_id: str, version: str, des_folder: str):
    local_repo_folder=get_config_folder(root=settings.local_repo_path, group_id=group_id, artifact_id=artifact_id, version=version, instance_id=None)
    from_local_repo_folder(local_repo_folder=local_repo_folder, artifact_id=artifact_id, version=version, des_folder=des_folder)


def from_local_repo_folder(local_repo_folder: str, artifact_id: str, version: str, des_folder: str):
    des=pathlib.Path(des_folder)
    # if des.is_dir():
    #     shutil.rmtree(str(des))
    des.mkdir(exist_ok=True, parents=True)
    shutil.copytree(local_repo_folder, des_folder, ignore=_ignore, copy_function=get_copy_from_repo_fn(artifact_id, version), dirs_exist_ok=True)


def to_local_repo(group_id: str, artifact_id: str, version: str, config_folder: str):
    local_repo_folder=get_config_folder(root=settings.local_repo_path, group_id=group_id, artifact_id=artifact_id, version=version, instance_id=None)
    version, _=versions.version_info(version)
    des=pathlib.Path(local_repo_folder)
    if des.is_dir():
        shutil.rmtree(str(des))
    des.mkdir(exist_ok=True, parents=True)
    shutil.copytree(config_folder, local_repo_folder, ignore=_ignore, copy_function=get_copy_to_repo_fn(artifact_id, version), dirs_exist_ok=True)
    pathlib.Path(local_repo_folder).joinpath(component_completion_flag).touch()


REMOTE_REPO_STATUS={
    'RepositoryCode.SUCCESS': 'Uploading Successful',
    'RepositoryCode.UNAUTHORIZED_UPLOAD': 'You are not authorized to upload assets',
    'RepositoryCode.UPLOAD_WITH_EMPTY_PATH': 'Uploading path should not be empty',
    'RepositoryCode.UPLOAD_WITH_ILLEGAL_ARTIFACT_ID': 'Illegal ArtifactId in uploading',
    'RepositoryCode.UPLOAD_WITH_ILLEGAL_VERSION': 'Illegal Version in uploading',
    'RepositoryCode.UPLOAD_WITH_ILLEGAL_CONFIG_FILE': 'Illegal config file in uploading',
    'RepositoryCode.FAILED': 'Uploading Failed. Maybe you are re-uploading a component to a release repository.'
}


def from_remote_repo(group_id: str, artifact_id: str, version: str):
    local_repo_folder=get_config_folder(root=settings.local_repo_path, group_id=group_id, artifact_id=artifact_id, version=version, instance_id=None)
    from_remote_repo_to_folder(local_repo_folder=local_repo_folder, group_id=group_id, artifact_id=artifact_id, version=version)


def from_remote_repo_to_folder(local_repo_folder: str, group_id: str, artifact_id: str, version: str):
    version, (main_version, info, snapshot)=versions.version_info(version)
    for repo in settings.repos:
        remote_repo_url=repo.repo_url(group_id=group_id, artifact_id=artifact_id, version=version, is_snapshot=snapshot)
        logger.info(f'Attempt to download {group_id}/{artifact_id}/{version} from `{remote_repo_url}`...')
        try:
            transfer.download_component(remote_repo_url, local_repo_folder)
            logger.info(f'Successfully downloaded {group_id}/{artifact_id}/{version} from remote repository.')
            return
        except PackageHttpException as e:
            logger.warning(e.msg+'\n')
    raise PackageException(f'Failed to downloaded {group_id}/{artifact_id}/{version} from remote repository.')


def to_remote_repo(session: Session, group_id: str, artifact_id: str, version: str, name: str, pwd: str, gpg=True, gpg_passphrase=None, gnupghome=None):
    local_repo_folder=get_config_folder(root=settings.local_repo_path, group_id=group_id, artifact_id=artifact_id, version=version, instance_id=None)
    version, _=versions.version_info(version)
    remote_repo_base_url=env.default_repo_base_url

    assets=[]
    metas=[]
    for file_name in os.listdir(local_repo_folder):
        file=os.path.join(local_repo_folder, file_name)
        if file_name!=component_completion_flag and os.path.isfile(file):
            ext=os.path.splitext(file)[1]
            if ext!='.asc':
                original_file_name=from_repo_file_name(file_name, artifact_id, version)
                assets.append((file, original_file_name))
                logger.info(f'checking component: {file_name} added')
                if gpg:
                    gpg_file=file+'.asc'
                    check.gpg(passphrase=gpg_passphrase, input_path=file, output_path=gpg_file, gnupghome=gnupghome)
                    metas.append((gpg_file, original_file_name+'.asc'))
                    logger.info(f'checking component: {file_name+".asc"} created and added')

    logger.info(f'Uploading {group_id}/{artifact_id}/{version} to remote repository...')
    try:
        response=transfer.upload_component(session=session, group_id=group_id, artifact_id=artifact_id, version=version, assets=assets, metas=metas, base_url=remote_repo_base_url, name=name, pwd=pwd)
        if response.status_code==200:
            data=response.json()
            if data['status']['code']==0:
                logger.info(f'{group_id}/{artifact_id}/{version} successfully uploaded.\n')
            else:
                logger.error(f'{group_id}/{artifact_id}/{version} uploading failed. Error message: {REMOTE_REPO_STATUS.get(data["status"]["des"])}\n')
        else:
            raise PackageHttpException(f'upload_component encounter HTTP error with code {response.status_code}.', response.status_code)
    except PackageException as e:
        logger.error(e.msg+'\n')


def retrieve_config(group_id: str, artifact_id: str, version: str, config_folder: str, config_file: str = None, force_update: bool = False) -> Tuple[str, str]:
    valid_config_file=None
    config_file_path=None
    default_config_file=None
    default_config_file_path=None
    local_repo_folder=None

    if force_update:
        exists=False
        default_exists=False
        local_repo_exists=False
    else:
        valid_config_file=config_file is not None and config_file.strip()!=''
        if valid_config_file:
            exists, config_file, config_file_path=check_config_file_existence(config_folder=config_folder, config_file=config_file)
        else:
            exists=False

        if exists:
            default_exists=True
            local_repo_exists=True
        else:
            default_exists, default_config_file, default_config_file_path=check_config_file_existence(config_folder=config_folder, config_file=None)
            if default_exists:
                local_repo_exists=True
            else:
                local_repo_folder=get_config_folder(root=settings.local_repo_path, group_id=group_id, artifact_id=artifact_id, version=version, instance_id=None)
                local_repo_exists, local_repo_config_file, local_repo_config_file_path=check_config_file_existence(config_folder=local_repo_folder, config_file=None, artifact_id=artifact_id, version=version, check_completion=True)

    if not local_repo_exists:
        logger.info(f'Downloading {group_id}/{artifact_id}/{version} from remote repository...')
        from_remote_repo_to_folder(local_repo_folder=local_repo_folder, group_id=group_id, artifact_id=artifact_id, version=version)
        logger.info(f'{group_id}/{artifact_id}/{version} successfully downloaded.')
        local_repo_exists, local_repo_config_file, local_repo_config_file_path=check_config_file_existence(config_folder=local_repo_folder, config_file=None, artifact_id=artifact_id, version=version, check_completion=True)
        if not local_repo_exists:
            raise PackageException(f'No valid config file in package: group_id={group_id}, artifact_id={artifact_id}, version={version}.')
    if not default_exists:
        logger.info(f'Retrieving {group_id}/{artifact_id}/{version} from local repository...')
        from_local_repo_folder(local_repo_folder=local_repo_folder, artifact_id=artifact_id, version=version, des_folder=config_folder)
        logger.info(f'{group_id}/{artifact_id}/{version} successfully retrieved.')
        default_exists, default_config_file, default_config_file_path=check_config_file_existence(config_folder=config_folder, config_file=None)
        if not default_exists:
            raise PackageException('Cannot copy config file from local repository to working folder.')
        if valid_config_file:
            exists, config_file, config_file_path=check_config_file_existence(config_folder=config_folder, config_file=config_file)
    if valid_config_file:
        if not exists:
            logger.info(f'Copy default config file to {config_file_path}')
            shutil.copy2(default_config_file_path, config_file_path)
            exists, config_file, config_file_path=check_config_file_existence(config_folder=config_folder, config_file=config_file)
            if not exists:
                raise PackageException(f'Cannot copy default config file to {config_file}.')
        logger.info(f'Config file "{config_file_path}" for "{group_id}/{artifact_id}/{version}" confirmed.')
        return config_file, config_file_path
    else:
        logger.info(f'Config file "{default_config_file_path}" for "{group_id}/{artifact_id}/{version}" confirmed.')
        return default_config_file, default_config_file_path
