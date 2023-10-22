# -*- coding: utf-8 -*-

import os
import pathlib
import hashlib
import gnupg


def md5(input_path, output_path=None):
    if not os.path.isfile(input_path):
        raise ValueError('Input is not a file.')

    with open(input_path, 'rb') as file:
        digest=hashlib.md5(file.read()).hexdigest()
    if output_path is not None:
        with open(output_path, 'w') as file:
            file.write(digest)
    return digest


def sha512(input_path, output_path=None):
    if not os.path.isfile(input_path):
        raise ValueError('Input is not a file.')

    with open(input_path, 'rb') as file:
        digest=hashlib.sha512(file.read()).hexdigest()
    if output_path is not None:
        with open(output_path, 'w') as file:
            file.write(digest)
    return digest


def gpg(passphrase, input_path, output_path=None, gnupghome=None):
    if not os.path.isfile(input_path):
        raise ValueError('Input is not a file.')

    gpg=gnupg.GPG(gnupghome=gnupghome if gnupghome else str(pathlib.Path.home().joinpath('.gnupg')))
    return gpg.sign_file(input_path, passphrase=passphrase, detach=True, output=output_path)
