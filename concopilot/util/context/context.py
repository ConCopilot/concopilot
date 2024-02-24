# -*- coding: utf-8 -*-

import uuid
import os
import re
import urllib.parse

from numbers import Number
from typing import Dict, List, Tuple, Sequence, Union, Mapping, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ...framework.interface import UserInterface

from ..class_dict import ClassDict
from ...framework.storage import Storage


class Asset(ClassDict):
    def __init__(
        self,
        *,
        asset_type: str,
        asset_id: Union[uuid.UUID, str, int] = None,
        asset_name: str = None,
        description: str = None,
        content_type: str = None,
        content: Any = None,
        **kwargs
    ):
        super(Asset, self).__init__(**kwargs)
        self.asset_type: str = asset_type
        self.asset_id: Union[uuid.UUID, str, int] = asset_id if asset_id else uuid.uuid4()
        self.asset_name: str = asset_name
        self.description: str = description
        self.content_type: str = content_type
        self.content: Any = content

    @staticmethod
    def convert_assets(assets: Dict[str, Dict]) -> ClassDict[str, 'Asset']:
        if not isinstance(assets, ClassDict):
            assets=ClassDict(**assets)
        update={}
        for k, v in assets.items():
            if not isinstance(v, Mapping):
                raise ValueError(f'assets contains non-mapping objects!')
            if not isinstance(v, Asset):
                update[k]=Asset(**ClassDict.convert(v))
        assets.update(update)
        return assets

    @staticmethod
    def get_meta(obj: Any) -> Union[ClassDict, List, Tuple, str, Number, bool]:
        if isinstance(obj, Mapping):
            return ClassDict(**{Asset.get_meta(k): Asset.get_meta(v) for k, v in obj.items()})
        elif isinstance(obj, List):
            return [Asset.get_meta(x) for x in obj]
        elif isinstance(obj, Tuple):
            return tuple(Asset.get_meta(x) for x in obj)
        elif isinstance(obj, (str, Number, bool)):
            return obj
        elif isinstance(obj, (uuid.UUID, os.PathLike)):
            return str(obj)
        else:
            return str(obj.__class__)

    def meta(self) -> ClassDict:
        return Asset.get_meta(self)

    @staticmethod
    def is_trivial(obj) -> bool:
        if isinstance(obj, Mapping):
            for k, v in obj.items():
                if not Asset.is_trivial(k) or not Asset.is_trivial(v):
                    return False
            return True
        elif isinstance(obj, (List, Tuple)):
            for x in obj:
                if not Asset.is_trivial(x):
                    return False
            return True
        elif isinstance(obj, (str, Number, bool, uuid.UUID, os.PathLike)):
            return True
        else:
            return False

    def trivial(self) -> bool:
        return Asset.is_trivial(self)


asset_ref_url_pattern=re.compile(r'^asset:/(/[^/]+)+/?$')


class AssetRef(ClassDict):
    def __init__(
        self,
        *,
        asset_id: Union[uuid.UUID, str, int],
        field_path: List[str] = None,
        **kwargs
    ):
        super(AssetRef, self).__init__(**kwargs)
        self.asset_id: Union[uuid.UUID, str, int] = asset_id
        self.field_path: List[str] = field_path

    @staticmethod
    def convert(asset_ref: Dict) -> 'AssetRef':
        return AssetRef(**ClassDict.convert(asset_ref))

    @staticmethod
    def convert_url(asset_ref_url: str) -> 'AssetRef':
        asset_url=urllib.parse.urlparse(asset_ref_url)
        if asset_url.scheme.lower()!='asset':
            raise ValueError('The asset reference url schema must be "asset"!')
        return AssetRef(
            asset_id=urllib.parse.unquote_plus(asset_url.hostname),
            field_path=[urllib.parse.unquote_plus(p) for p in asset_url.path.strip('/').split('/')]
        )

    @staticmethod
    def asset_ref_like(obj: Any) -> bool:
        """
        Check if the input `obj` looks like an `AssetRef` instance.
        That is, the `obj` is a Mapping instance, and contains both an 'asset_id' key and 'field_path' key.

        :param obj: the input object to be checked.
        :return: True if the input object looks like an AssetRef, otherwise False.
        """
        return isinstance(obj, Mapping) and isinstance(obj.get('asset_id'), str) and isinstance(obj.get('field_path'), List)

    @staticmethod
    def asset_ref_url_like(obj: Any) -> bool:
        """
        Check if the input `obj` looks like an `AssetRef` url.
        That is, the `obj` is a url string with scheme "asset".

        :param obj: the input object to be checked.
        :return: True if the input object looks like an AssetRef url, otherwise False.
        """
        return isinstance(obj, str) and asset_ref_url_pattern.match(obj)

    @staticmethod
    def try_convert(obj: Any) -> Optional['AssetRef']:
        """
        Try to convert the input `obj` into an `AssetRef` instance.
        If it cannot be converted, a `None` will be returned.

        :param obj: the input object to be tried to convert.
        :return: The converted result if success, otherwise None.
        """
        if AssetRef.asset_ref_like(obj):
            return AssetRef.convert(obj)
        elif AssetRef.asset_ref_url_like(obj):
            return AssetRef.convert_url(obj)
        else:
            return None

    @staticmethod
    def try_retrieve(obj: Any, assets: ClassDict[str, Asset]) -> Any:
        """
        Try to retrieve an asset field value from an asset that can be represented by the input AssetRef-like `obj` and presents in the given `assets` mapping.
        The `obj` itself will be returned if it is not an AssetRef-like object.
        However, an exception will be raised if either no such asset found in the `assets` mapping or the asset has been found but the given `field_path` is incorrect.

        :param obj: the input, either an AssetRef-like `obj` to locate the asset, or any object.
        :param assets: the asset mapping.
        :return: the retrieved field located at obj['field_path'] from the asset represented by the obj['asset_id'], or the obj itself if it is not an AssetRef-like object.
        """
        if asset_ref:=AssetRef.try_convert(obj):
            return asset_ref.retrieve(assets)
        else:
            return obj

    def retrieve(self, assets: ClassDict[str, Asset]):
        asset_id=str(self.asset_id)
        if asset_id in assets:
            value=assets[asset_id]
            if self.field_path:
                level=0
                for key in self.field_path:
                    if hasattr(value, key):
                        value=getattr(value, key)
                    elif isinstance(value, Mapping):
                        if key in value:
                            value=value[key]
                        else:
                            raise ValueError(f'The asset object at `{self.to_asset_ref_url(level)}` does not contains key `{key}`, only `{[key for key in value.keys()]}` are available! Try to correct the AssetRef `field_path`.')
                    elif isinstance(value, Sequence):
                        try:
                            value=value[int(key)]
                        except ValueError:
                            raise ValueError(f'`{key}` cannot be converted to an `int`, so that it cannot index the asset sequence at `{self.to_asset_ref_url(level)}`! Try to correct the AssetRef `field_path`.')
                        except IndexError:
                            raise ValueError(f'Index `{key}` is out of range of the asset sequence at `{self.to_asset_ref_url(level)}`! Try to correct the AssetRef `field_path`.')
                    else:
                        raise ValueError(f'The asset object at `{self.to_asset_ref_url(level)}` with type `{value.__class__}` has no attribute `{key}`, and is neither a Mapping object nor a Sequence object, so that cannot be indexed by key `{key}`! Try to correct the AssetRef `field_path`.')
                    level+=1
            return value
        else:
            raise ValueError(f'No such asset found with asset_id `{asset_id}`')

    def to_asset_ref_url(self, level: int = -1):
        return f'asset://{urllib.parse.quote(self.asset_id)}/{"/".join([urllib.parse.quote(p) for p in self.field_path[:(level if level>=0 else len(self.field_path))]])}'.strip('/')

    def __str__(self):
        return self.to_asset_ref_url()


class Context(ClassDict):
    def __init__(self, *, storage: Storage = None, assets: Dict[str, Asset] = None, user_interface: 'UserInterface' = None, **kwargs):
        super(Context, self).__init__(**kwargs)
        self.storage: Storage = storage
        self.assets: ClassDict[str, Asset] = Asset.convert_assets(assets)
        self.user_interface: 'UserInterface' = user_interface
