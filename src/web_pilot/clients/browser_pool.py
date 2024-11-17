import uuid
import pydantic as pyd

from typing import Optional
from web_pilot.config import config as conf
from web_pilot.clients.browser import LeasedBrowser
from web_pilot.exc import (
    BrowserPoolCapacityReachedError,
    NoAvailableBrowserError,
)
from web_pilot.utils.decorators import run_if_browser_accepts_new_jobs
from web_pilot.logger import logger


class BrowserPool:
    id_: str
    config_template: dict
    _pool: dict[uuid.UUID, LeasedBrowser]
    _max_browsers: int
    _least_busy_browser_idx: int
    _accepts_new_jobs: bool

    @pyd.validate_arguments
    def __init__(self, pool_id: str, config: dict) -> None:
        self.id_ = pool_id
        self.config_template = config  # used as a template to instantiate new browsers in the pool
        self._pool = {}
        self._max_browsers = conf.pool_max_size
        self._least_busy_browser_idx = 0  # Round-robin index
        self._accepts_new_jobs = True

    def __str__(self) -> str:
        return f"BrowserPool(id={self.id_.__str__()}, browser_count={len(self._pool)}, max_browsers={self._max_browsers}, total_pages={sum([browser.page_count for browser in self._pool.values()])})"

    def __repr__(self) -> dict:
        return dict(
            id=self.id_.__str__(),
            browser_count=len(self._pool),
            max_browsers=self._max_browsers,
            total_pages=sum([browser.page_count for browser in self._pool.values()]),
            is_idle=self.is_idle,
            accepts_new_jobs=self._accepts_new_jobs,
            config=self.config_template,
        )

    @property
    def browsers(self) -> list[LeasedBrowser]:
        return list(self._pool.values())

    @property
    def is_idle(self) -> bool:
        return all([browser.is_idle for browser in self._pool.values()])

    def mark_as_inactive(self) -> None:
        self._accepts_new_jobs = False

    @run_if_browser_accepts_new_jobs
    def create_new_browser(self) -> LeasedBrowser:
        "Create and return a new browser instance"
        browser_id = len(self._pool)
        if len(self._pool) >= self._max_browsers:
            raise BrowserPoolCapacityReachedError(
                f"Max number of browsers in pool reached: {self._max_browsers}"
            )
        new_browser = LeasedBrowser(browser_id, parent=self.id_, **self.config_template)
        self._pool[browser_id] = new_browser
        return new_browser

    @pyd.validate_arguments
    @run_if_browser_accepts_new_jobs
    def remove_browser_by_id(self, browser_id: uuid.UUID, force: bool = False) -> bool:
        "Remove browser from pool by its ID"
        if browser_id not in self._pool or not force and self._pool[browser_id].page_count > 0:
            return False

        self._pool[browser_id].browser.close()
        del self._pool[browser_id]
        return True

    @pyd.validate_arguments
    @run_if_browser_accepts_new_jobs
    def get_browser_by_id(self, browser_id: int) -> Optional[LeasedBrowser]:
        "Get browser by its ID"
        return self._pool.get(browser_id)

    @run_if_browser_accepts_new_jobs
    async def get_least_busy_browser(self) -> LeasedBrowser:
        """
        Get the next available browser in the pool.
        If all browsers are full, raises an `NoAvailableBrowserError` exception.
        """
        if len(self.browsers) == 0:
            return self.create_new_browser()

        elif len(self.browsers) == 1:
            return self._pool[0]

        least_busy_browser_idx = 0
        for idx, browser in enumerate(self.browsers):
            if (
                not browser.is_idle
                and browser.page_count > 0
                and browser.page_count < self.browsers[least_busy_browser_idx].page_count
            ):
                least_busy_browser_idx = idx

        if browser := self.browsers[least_busy_browser_idx].has_capacity:
            self._least_busy_browser_idx = least_busy_browser_idx
            return browser

        # If all browsers are full, attempt to scale up else raise an exception
        if new_browser := self.scale_up():
            self._least_busy_browser_idx = (self._least_busy_browser_idx + 1) % len(self.browsers)
            return new_browser

        raise NoAvailableBrowserError(
            "All browsers are currently at full capacity! try again later."
        )

    def scale_up(self) -> Optional[LeasedBrowser]:
        try:
            return self.create_new_browser()
        except BrowserPoolCapacityReachedError as e:
            logger.bind(pool_id=self.id_, action="scale_up").info(e)
            return None

    def scale_down(self) -> None:
        ...
