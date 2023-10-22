# -*- coding: utf-8 -*-

from ..util.error import ConcopilotError


class PackageException(ConcopilotError):
    def __init__(self, msg: str):
        super(PackageException, self).__init__(msg)


class PackageHttpException(PackageException):
    def __init__(self, msg: str, http_code: int):
        super(PackageHttpException, self).__init__(msg)
        self.http_code=http_code


class PackageServiceException(PackageException):
    def __init__(self, msg: str, status_code: int, status_des: str):
        super(PackageServiceException, self).__init__(msg)
        self.status_code=status_code
        self.status_des=status_des
