import uuid
import pydantic as pyd
import functools
import asyncio

from typing import Optional
from web_pilot.config import config as conf
from web_pilot.clients.browser import LeasedBrowser
from web_pilot.exc import (
    BrowserPoolCapacityReachedError,
    NoAvailableBrowserError,
    PoolIsInactiveError,
)


class BrowserPool:
    id_: str
    config_template: dict
    _pool: dict[uuid.UUID, LeasedBrowser]
    _max_browsers: int
    _rr_current_index: int
    _accept_new_jobs: bool

    @pyd.validate_arguments
    def __init__(self, pool_id: str, config: dict) -> None:
        self.id_ = pool_id
        self.config_template = config  # used as a template to instantiate new browsers in the pool
        self._pool = {}
        self._max_browsers = conf.pool_max_size
        self._rr_current_index = 0  # Round-robin index
        self._accept_new_jobs = True

    @property
    def id(self) -> str:
        return self.id_

    @id.setter
    def id(self, value: str) -> None:
        self.id_ = value

    def __repr__(self) -> str:
        return f"BrowserPool(id={self.id_.__str__()}, browser_count={len(self._pool)}, max_browsers={self._max_browsers}, total_pages={sum([browser.page_count() for browser in self._pool.values()])})"

    @property
    def browsers(self) -> list[LeasedBrowser]:
        return list(self._pool.values())

    @property
    def is_busy(self) -> bool:
        return any([browser.page_count() > 0 for browser in self._pool.values()])

    def _only_if_accept_new_jobs(func) -> callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self._accept_new_jobs:
                raise PoolIsInactiveError("Pool is inactive")

            # Check at call time whether to use async or sync execution
            if asyncio.iscoroutinefunction(func):
                # Use an inner async function when called in an async context
                async def async_wrapper():
                    return await func(self, *args, **kwargs)

                return async_wrapper()  # Call immediately, returns a coroutine

            # Otherwise, just call synchronously
            return func(self, *args, **kwargs)

        return wrapper

    def mark_as_inactive(self) -> None:
        self._accept_new_jobs = False

    @_only_if_accept_new_jobs
    def create_new_browser(self) -> str:
        "Create and return a new browser instance"
        browser_id = len(self._pool)
        if len(self._pool) >= self._max_browsers:
            raise BrowserPoolCapacityReachedError(
                f"Max number of browsers in pool reached: {self._max_browsers}"
            )
        self._pool[browser_id] = LeasedBrowser(browser_id, parent=self.id_, **self.config_template)
        return browser_id

    @pyd.validate_arguments
    @_only_if_accept_new_jobs
    def remove_browser_by_id(self, browser_id: uuid.UUID, force: bool = False) -> bool:
        "Remove browser from pool by its ID"
        if browser_id not in self._pool or not force and self._pool[browser_id].page_count() > 0:
            return False

        self._pool[browser_id].browser.close()
        del self._pool[browser_id]
        return True

    @pyd.validate_arguments
    @_only_if_accept_new_jobs
    def get_browser_by_id(self, browser_id: int) -> Optional[LeasedBrowser]:
        "Get browser by its ID"
        return self._pool.get(browser_id)

    @_only_if_accept_new_jobs
    async def get_next_browser(self) -> LeasedBrowser:
        """
        Get the next available browser in the pool - round-robin.
        If all browsers are full, raises an `NoAvailableBrowserError` exception.
        This method is used if `balance_load` is set to `True`.
        """
        if len(self.browsers) == 0:
            self.create_new_browser()
            return self._pool[0]

        elif len(self.browsers) == 1:
            return self._pool[0]

        for _ in range(len(self.browsers)):
            browser: LeasedBrowser = self.browsers[self._rr_current_index]
            # Check if browser has capacity for more pages
            if browser.page_count < conf.max_cached_items:
                self._rr_current_index = (self._rr_current_index + 1) % len(self.browsers)
                return browser
            # Move to the next browser
            self._rr_current_index = (self._rr_current_index + 1) % len(self.browsers)

        # If all browsers are full, raise an exception
        # TODO: implement optional wait logic
        raise NoAvailableBrowserError("All browsers are currently at capacity.")

    # def scale_up(cls):
    #     if len(cls._pool) < cls.max_browsers:
    #         return cls.create_new_browser()
