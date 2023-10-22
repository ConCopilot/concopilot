# -*- coding: utf-8 -*-

import hashlib
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
import base64


def scrypt(pwd: bytes, salt: bytes = b'') -> bytes:
    scrypted=hashlib.scrypt(password=pwd, salt=salt, n=16384, r=8, p=1, dklen=256)
    return base64.b64encode(scrypted)


def encrypt_RSA(msg: bytes, public_key: bytes) -> str:
    encryptor=PKCS1_v1_5.new(RSA.importKey(public_key))
    encrypted=encryptor.encrypt(msg)
    return base64.b64encode(encrypted).decode('ISO_8859_1')
