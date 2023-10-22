# -*- coding: utf-8 -*-

import pathlib
import shutil

from typing import AnyStr

from ...resource import Resource
from ....package.config import Settings


settings=Settings()


class Disk(Resource):
    def __init__(self, config):
        super(Disk, self).__init__(config)
        assert self.resource_type=='disk'
        self.root: pathlib.Path = pathlib.Path(self.config.config.root_directory if self.config.config.root_directory else (settings.working_directory if settings.working_directory else '.')).absolute()

    def read_file(self, path: str, binary: bool = False) -> AnyStr:
        abs_path=self._check_in_root(path)
        if not abs_path.is_file():
            raise FileNotFoundError('File not exists')
        return abs_path.read_bytes() if binary else abs_path.read_text(encoding='utf8')

    def write_file(self, path: str, value: AnyStr) -> int:
        abs_path=self._check_in_root(path)
        if abs_path.is_dir():
            raise FileNotFoundError('Target is a directory')
        abs_path.parent.mkdir(exist_ok=True, parents=True)
        return abs_path.write_bytes(value) if isinstance(value, bytes) else abs_path.write_text(value, encoding='utf8')

    def delete_file(self, path: str):
        abs_path=self._check_in_root(path)
        if abs_path.is_file():
            abs_path.unlink()
        else:
            raise FileNotFoundError('File not exists')

    def delete_folder(self, path: str):
        abs_path=self._check_in_root(path)
        if abs_path.is_dir():
            shutil.rmtree(str(abs_path))
        else:
            raise FileNotFoundError('Directory not exists')

    def _check_in_root(self, path) -> pathlib.Path:
        abs_path=pathlib.Path(path).absolute()
        if abs_path.is_relative_to(self.root) and abs_path!=self.root:
            return abs_path
        else:
            raise ValueError(f'Input path ({path}) does not represent a position under the root path ({self.root})')

    def initialize(self):
        pass

    def finalize(self):
        pass
