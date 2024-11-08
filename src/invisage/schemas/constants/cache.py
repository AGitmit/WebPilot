from enum import Enum


class CacheType(Enum):
    TTL = "ttl"
    # LRU = "lru"
    # RRC = "rrc"


class CacheProvider(Enum):
    IN_MEMORY = "in_memory"
