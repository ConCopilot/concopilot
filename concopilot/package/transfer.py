# -*- coding: utf-8 -*-

import os
import requests
import pathlib
import yaml
import tqdm
import urllib.parse

from typing import List, Tuple

from . import request
from .config import Settings, component_completion_flag
from .error import PackageHttpException


settings=Settings()


def upload_component(session: requests.Session, group_id: str, artifact_id: str, version: str, assets: List[Tuple[str, str]], metas: List[Tuple[str, str]], base_url: str, name: str, pwd: str):
    auth=request.Auth(session=session, base_url=base_url, name=name, pwd=pwd)
    return request.request_upload(session=session, url=base_url+'/api/repo/upload', b={
        'g': group_id,
        'a': artifact_id,
        'v': version
    }, assets=assets, metas=metas, auth=auth)


def download_component(remote_repo_url, local_repo_folder):
    requester=settings.network_session if settings.network_session else requests
    response=requester.post(remote_repo_url)
    if response.status_code==200:
        file_list=yaml.safe_load(response.text)
        for file in file_list:
            file_url=urllib.parse.urljoin(remote_repo_url+'/', pathlib.Path(file).name)
            download_file(requester, file_url, local_repo_folder)
        pathlib.Path(local_repo_folder).joinpath(component_completion_flag).touch()
    else:
        raise PackageHttpException(f'No such resources found in url `{remote_repo_url}`', http_code=response.status_code)


def download_file(requester, url, folder):
    file_name=os.path.basename(urllib.parse.urlparse(url).path)
    file_name=os.path.join(folder, file_name)
    response=requester.get(url, stream=True)
    total_length=int(response.headers.get('content-length'))
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(file_name, 'wb') as file:
        with tqdm.tqdm(total=total_length, unit='B', unit_scale=True, unit_divisor=1024, desc=f'Downloading {file_name}: ') as t:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    t.update(len(chunk))
