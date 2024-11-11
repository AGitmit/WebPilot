import uuid
import pydantic as pyd

from typing import Optional


class PoolAdmin:
    _pools: dict = {}

    @classmethod
    @pyd.validate_arguments
    def get_pool(cls, pool_id: uuid.UUID) -> Optional[dict]:
        "Get pool by its ID"
        return cls._pools.get(pool_id)

    # @classmethod
    # @pyd.validate_arguments
    # def get_all_pools(cls) -> dict:
    #     "Get all pools"
    #     return cls._pools

    @classmethod
    @pyd.validate_arguments
    def delete_pool(cls, pool_id: uuid.UUID, force: bool = False) -> bool:
        "Remove pool by its ID"
        if pool_id not in cls._pools:
            return False
        # TODO: implement optional wait logic (if pool is not empty and 'force' is False)
        del cls._pools[pool_id]
        return True

    @classmethod
    @pyd.validate_arguments
    def create_new_pool(cls) -> uuid.UUID:
        "Create new pool instance, return it's ID for reference"
        pool_id = uuid.uuid4().__str__()
        cls._pools[pool_id] = {}
        return pool_id
