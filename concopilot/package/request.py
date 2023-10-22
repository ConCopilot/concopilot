# -*- coding: utf-8 -*-
import base64

import requests
import uuid
import json
import os
import datetime

from . import encrypt
from . import captcha
from .error import PackageException, PackageHttpException, PackageServiceException
from ..util.jsons import JsonEncoder


def get_c():
    request_id=uuid.uuid4()
    return {
        'rId': request_id,
        'tId': request_id
    }


def request_post(session: requests.Session, url, b, c=None):
    if c is None:
        c=get_c()
    return send(session=session, method='post', url=url, b=b, c=c, headers=None, files=None, auth=None)


def request_upload(session: requests.Session, url, b, assets, metas, auth):
    def append_file(files, key, file_info_list):
        for file_path, name in file_info_list:
            with open(file_path, 'rb') as file:
                file_data=file.read()
            files.append([key, (name if name is not None else os.path.basename(file_path), file_data)])
        return files

    c=get_c()
    files=[]
    append_file(files, 'assets', assets)
    append_file(files, 'metas', metas)
    return send(session=session, method='post', url=url, b=b, c=c, headers=None, files=files, auth=auth)


def send(session: requests.Session, method, url, b, c, headers=None, files=None, auth=None):
    return session.request(method=method, url=url, data={
        'b': json.dumps(b, cls=JsonEncoder, ensure_ascii=False),
        'c': json.dumps(c, cls=JsonEncoder, ensure_ascii=False)
    }, headers=headers, files=files, auth=auth)


def request_public_key(session: requests.Session, url, captcha):
    response=request_post(session=session, url=url, b={'captcha': captcha})
    if response.status_code==200:
        data=response.json()
        if data['status']['code']==0:
            return data['data']
        else:
            raise PackageServiceException('request_public_key failed.', response.status_code, response.text)
    else:
        raise PackageHttpException(f'request_public_key encounter HTTP error with code {response.status_code}.', response.status_code)


def captcha_url(base_url):
    return f'{base_url}/api/captcha?d={int(datetime.datetime.now().timestamp()*1000)}'


def login(session: requests.Session, base_url, name, pwd):
    captcha_client=captcha.CaptchaClient(request_fn=captcha.get_request_fn(session=session, captcha_url=captcha_url(base_url)))
    captcha_client.open()
    public_key=request_public_key(session=session, url=base_url+'/api/key', captcha=captcha_client.captcha_text)
    key=encrypt.scrypt(pwd.encode('utf8'))
    key=encrypt.encrypt_RSA(key, base64.decodebytes(public_key.encode('ascii')))
    response=request_post(session=session, url=base_url+'/api/login', b={'name': name, 'pwd': key})
    if response.status_code==200:
        data=response.json()
        if data['status']['code']!=0:
            raise PackageServiceException('login failed.', response.status_code, response.text)
    else:
        raise PackageHttpException(f'login encounter HTTP error with code {response.status_code}.', response.status_code)


def check_login(session: requests.Session, base_url):
    response=session.post(base_url+'/api/checklogin')
    if response.status_code==200:
        data=response.json()
        return 'data' in data
    else:
        raise PackageHttpException(f'check_login encounter HTTP error with code {response.status_code}.', response.status_code)


class Auth(requests.auth.AuthBase):
    def __init__(self, session: requests.Session, base_url: str, name: str, pwd: str):
        super(Auth, self).__init__()
        self.session=session
        self.base_url=base_url
        self.name=name
        self.pwd=pwd

    def __call__(self, r):
        try:
            if not check_login(self.session, self.base_url):
                login(session=self.session, base_url=self.base_url, name=self.name, pwd=self.pwd)
                r.prepare_cookies(self.session.cookies)
        except PackageServiceException:
            raise PackageException('Authorization Failed! Please check your user name, password, and captcha.')
        except PackageHttpException as e:
            raise PackageHttpException(f'Authorization Failed! Service reture status code {e.http_code}. Please try again later.', e.http_code)
        return r

