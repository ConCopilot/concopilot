# -*- coding: utf-8 -*-

import os
import pathlib
import yaml
import validators
import urllib.parse
import datetime
import requests

from typing import Dict, List, Callable, Optional

from ..util.singleton import Singleton


class Env(Singleton):
    def __init__(self):
        self.default_settings_path: str = str(pathlib.Path.home().joinpath('.concopilot/settings.yaml'))

        self.default_local_repo_path: str = str(pathlib.Path.home().joinpath('.concopilot/repository'))
        # default_repo_url/snapshots for snapshot
        # default_repo_url/releases for release
        self.default_repo_base_url: str = 'https://concopilot.org'


def curr_time() -> str:
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


class Settings(Singleton):
    class Repo:
        class RepoPolicy:
            def __init__(self, enable: bool, update: bool):
                self.enable: bool = enable
                self.update: bool = update

        def __init__(self, url: str, snapshot: RepoPolicy = None, release: RepoPolicy = None):
            if not validators.url(url, simple_host=True):
                raise ValueError('Invalid url: '+str(url))
            self.url: str = url
            self.snapshot: Settings.Repo.RepoPolicy = snapshot if snapshot is not None else Settings.Repo.RepoPolicy(enable=True, update=True)
            self.release: Settings.Repo.RepoPolicy = release if release is not None else Settings.Repo.RepoPolicy(enable=True, update=False)

        def _repo_url(self, repo_name: str, group_id: str = None, artifact_id: str = None, version: str = None) -> str:
            if group_id is None and artifact_id is None and version is None:
                return urllib.parse.urljoin(env.default_repo_base_url, repo_name)
            elif group_id is not None and artifact_id is not None and version is not None:
                return urllib.parse.urljoin(env.default_repo_base_url, f'/repository/{repo_name}/{group_id.replace(".", "/")}/{artifact_id}/{version}')
            elif group_id is not None and artifact_id is not None:
                return urllib.parse.urljoin(env.default_repo_base_url, f'/repository/{repo_name}/{group_id.replace(".", "/")}/{artifact_id}')
            elif group_id is not None:
                return urllib.parse.urljoin(env.default_repo_base_url, f'/repository/{repo_name}/{group_id.replace(".", "/")}')
            else:
                raise ValueError(f'Cannot get url from an invalid combination of group_id({group_id}), artifact_id({artifact_id}), and version ({version})')

        def snapshot_url(self, group_id: str = None, artifact_id: str = None, version: str = None) -> str:
            return self._repo_url(repo_name='snapshots', group_id=group_id, artifact_id=artifact_id, version=version)

        def release_url(self, group_id: str = None, artifact_id: str = None, version: str = None) -> str:
            return self._repo_url(repo_name='releases', group_id=group_id, artifact_id=artifact_id, version=version)

        def repo_url(self, group_id: str = None, artifact_id: str = None, version: str = None, is_snapshot: bool = False) -> str:
            if is_snapshot:
                return self.snapshot_url(group_id=group_id, artifact_id=artifact_id, version=version)
            else:
                return self.release_url(group_id=group_id, artifact_id=artifact_id, version=version)

        @staticmethod
        def convert(d: Dict):
            url: str = d.get('url')
            snapshot=d.get('snapshot')
            if snapshot is not None:
                if isinstance(snapshot, Dict):
                    snapshot=Settings.Repo.RepoPolicy(enable=snapshot.get('enable'), update=snapshot.get('update'))
                elif not isinstance(snapshot, Settings.Repo.RepoPolicy):
                    raise ValueError('Unrecognized snapshot repo')
            release=d.get('release')
            if release is not None and not isinstance(release, Settings.Repo.RepoPolicy):
                if isinstance(release, Dict):
                    release=Settings.Repo.RepoPolicy(enable=release.get('enable'), update=release.get('update'))
                elif not isinstance(release, Settings.Repo.RepoPolicy):
                    raise ValueError('Unrecognized release repo')
            return Settings.Repo(url, snapshot, release)

    def __init__(self, local_repo_path: str = None, repos: List[Repo] = None, working_directory: str = '.', skip_setup: bool = False, pip_params: List = None, current_time: Callable[[], str] = None):
        self.local_repo_path: str = check_local_repo_path(local_repo_path=local_repo_path)
        self.repos: List[Settings.Repo] = check_repos(repos=repos)
        self.working_directory: str = working_directory if working_directory else '.'
        self.skip_setup: bool = skip_setup
        self.pip_params: List = pip_params if pip_params is not None else []
        self._current_time: Callable[[], str] = current_time if current_time else curr_time

        self.network_session: Optional[requests.Session] = None

    @property
    def current_time(self) -> Callable[[], str]:
        return self._current_time

    @current_time.setter
    def current_time(self, value: Callable[[], str]):
        self._current_time=value if value else curr_time


env=Env()
default_repo=Settings.Repo(url=env.default_repo_base_url)


default_config_folder='.config'
default_config_files=['config.yaml', 'config.yml']
component_completion_flag='__COMPLETED'


def check_local_repo_path(local_repo_path: str = None):
    return local_repo_path if local_repo_path is not None else env.default_local_repo_path


def check_repos(repos: List[Settings.Repo] = None):
    repos: List[Settings.Repo] = repos if repos is not None else []
    if len(repos)==0:
        repos.append(default_repo)
    return repos


def load_settings(settings_path: str = None, working_directory: str = None, skip_setup: str = None, pip_params: str = None) -> Settings:
    settings=Settings()

    settings_info=None
    settings_path=settings_path if settings_path is not None else env.default_settings_path
    if os.path.isfile(settings_path):
        with open(settings_path) as file:
            settings_info=yaml.safe_load(file)

    if settings_info is not None:
        if 'local_repo_path' in settings_info:
            settings.local_repo_path=check_local_repo_path(settings_info['local_repo_path'])
        if 'repos' in settings_info:
            settings.repos=check_repos([Settings.Repo.convert(repo) for repo in settings_info['repos'] if repo is not None])

    if working_directory is not None:
        settings.working_directory=working_directory
    if skip_setup is not None:
        settings.skip_setup=skip_setup
    if pip_params:
        pip_params=[param for param in pip_params.split(' ') if param]
        settings.pip_params=pip_params

    return settings
