import pydantic as pyd
import cachetools

from typing import Union
from invisage.schemas.constants.cache import CacheProvider
from invisage.config import config as conf


class CacheUtil:
    _provider = None
    _max_items = conf.max_cached_items
    _ttl = conf.cache_ttl

    @classmethod
    def _get_provider(cls) -> Union[cachetools.TTLCache]:
        if cls._provider is None:
            match conf.cache_provider:
                case CacheProvider.IN_MEMORY:
                    cls._provider = cachetools.TTLCache(
                        maxsize=conf.max_cached_items, ttl=conf.cache_ttl
                    )
                case _:
                    raise ValueError("Unknown cache provider")
        return cls._provider

    @classmethod
    def get_item(cls, key: str):
        return cls._get_provider().__getitem__(key)

    @classmethod
    def set_item(cls, key: str, value: pyd.BaseModel) -> None:
        cls._get_provider().__setitem__(key, value)

    @classmethod
    def delete_item(cls, key: str) -> None:
        cls._get_provider().__delitem__(key)
