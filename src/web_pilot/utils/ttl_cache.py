import pydantic as pyd
import cachetools

from typing import Union
from web_pilot.schemas.constants.cache import CacheProvider
from web_pilot.config import config as conf


class TTLCache:
    def __init__(self) -> None:
        self._cache = self._init_cache(max_items=conf.max_cached_items, ttl=conf.cache_ttl)

    def _init_cache(self, max_items: int = None, ttl: int = None) -> Union[cachetools.TTLCache]:
        match conf.cache_provider:
            case CacheProvider.IN_MEMORY:
                return cachetools.TTLCache(maxsize=max_items, ttl=ttl)
            case _:
                raise ValueError("Unsupported cache provider")

    def __len__(self) -> int:
        return len(self._cache)

    def get_item(self, key: str):
        return self._cache.__getitem__(key)

    def pop_item(self, key: str):
        return self._cache.pop(key)

    def set_item(self, key: str, value: pyd.BaseModel) -> None:
        self._cache.__setitem__(key, value)

    def delete_item(self, key: str) -> None:
        self._cache.__delitem__(key)
