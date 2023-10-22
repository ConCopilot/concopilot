# -*- coding: utf-8 -*-

import re


def version_info(version):
    if version[-9:].upper()=='-SNAPSHOT':
        version=version[:-9]+'-SNAPSHOT'
        ver=version[:-9]
        snapshot=True
    else:
        ver=version
        snapshot=False
    pattern=re.compile(r'^(\d+(?:\.\d+)*)(?:-([^`~!@#$%^&*()\[\]{}\\|;:\'",/?]+))?$')
    if result:=pattern.match(ver):
        main_version, info=result.groups()
        return version, (main_version, info, snapshot)
    else:
        raise ValueError('Illegal version format')


def sort_versions(versions):
    def key_fn(item):
        _, (main_version, info, snapshot)=item
        return tuple(-int(x) for x in main_version.split('.')), info if info else '', snapshot

    version_info_list=[version_info(ver) for ver in versions]
    version_info_list.sort(key=key_fn)
    return version_info_list
