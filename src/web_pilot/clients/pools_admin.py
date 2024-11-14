import uuid
import pydantic as pyd

from hashlib import sha1
from typing import Optional
from web_pilot.logger import logger
from web_pilot.clients.browser_pool import BrowserPool
from web_pilot.exc import PoolAlreadyExistsError, PageSessionNotFoundError
from web_pilot.clients.browser import LeasedBrowser


class PoolAdmin:
    _pools: dict = {}
    _deletion_candidates: list[uuid.UUID] = []

    @classmethod
    def list_pools(cls) -> list[BrowserPool]:
        return list(cls._pools.values())

    @classmethod
    @pyd.validate_arguments
    def get_pool(cls, pool_id: str) -> Optional[BrowserPool]:
        "Get pool by its ID"
        return cls._pools.get(pool_id)

    @classmethod
    @pyd.validate_arguments
    def get_session_owners_chain(cls, session_id: str) -> Optional[LeasedBrowser]:
        "Get session owners chain by session ID"
        pool_id, browser_id, page_id = tuple(session_id.split("_"))
        try:
            pool = cls.get_pool(pool_id)
            browser = pool.get_browser_by_id(int(browser_id))
            page = browser.retrieve_page_session(int(page_id))
            return pool, browser, page

        except Exception:
            raise PageSessionNotFoundError("Page session not found")

    # @classmethod
    # @pyd.validate_arguments
    # def get_all_pools(cls) -> dict:
    #     "Get all pools"
    #     return cls._pools

    @classmethod
    @pyd.validate_arguments
    def delete_pool(cls, pool_id: str, force: bool = False) -> bool:
        "Remove pool by its ID"
        if pool_id not in cls._pools:
            return False

        if force:
            del cls._pools[pool_id]
        else:
            cls._deletion_candidates.append(pool_id)
            cls._pools[pool_id].mark_as_inactive()
        return True

    @classmethod
    @pyd.validate_arguments
    def remove_deletion_candidates(cls) -> None:
        logger.debug("Removing pools marked for deletion...")
        for p_idx, pool_id in enumerate(cls._deletion_candidates):
            if pool_id not in cls._pools or cls._pools[pool_id].is_busy:
                logger.bind(pool_id=pool_id).info(
                    "Is candidate for deletion, but is currently busy - skipping deletion"
                )
                continue
            del cls._pools[pool_id]
            cls._deletion_candidates.pop(p_idx)
            logger.bind(pool_id=pool_id).info("Pool deleted successfully")

    @classmethod
    @pyd.validate_arguments
    def create_new_pool(cls, config: dict = {}) -> uuid.UUID:
        "Create new pool instance, return it's ID for reference"
        pool_id = sha1(str(config).encode()).hexdigest()
        if pool_id in cls._pools:
            raise PoolAlreadyExistsError(
                f"A pool with these configuration already exists - pool_id:'{pool_id}'"
            )
        cls._pools[pool_id] = BrowserPool(pool_id, config)
        return pool_id
