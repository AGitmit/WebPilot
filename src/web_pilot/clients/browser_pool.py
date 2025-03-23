import uuid
import pydantic as pyd

from typing import Optional
from web_pilot.config import config as conf
from web_pilot.clients.leased_browser import LeasedBrowser
from web_pilot.exc import (
    BrowserPoolCapacityReachedError,
    NoAvailableBrowserError,
)
from web_pilot.utils.decorators import run_if_pool_accepts_new_jobs
from web_pilot.logger import logger
from web_pilot.utils.sessions import generate_id


class BrowserPool:
    id_: str
    config_template: dict
    _pool: dict[uuid.UUID, LeasedBrowser]
    _max_browsers: int
    _accepts_new_jobs: bool

    @pyd.validate_arguments
    def __init__(self, pool_id: str, config: dict) -> None:
        self.id_ = pool_id
        self.config_template = config  # used as a template to instantiate new browsers in the pool
        self._pool = {}
        self._max_browsers = conf.browser_pool_max_size
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

    @run_if_pool_accepts_new_jobs
    def create_new_browser(self) -> LeasedBrowser:
        "Create and return a new browser instance"
        browser_id = generate_id()
        if len(self._pool) >= self._max_browsers:
            raise BrowserPoolCapacityReachedError(
                f"Max number of browsers in pool reached: {self._max_browsers}"
            )
        new_browser = LeasedBrowser(browser_id, parent=self.id_, **self.config_template)
        self._pool[browser_id] = new_browser
        logger.bind(pool_id=self.id_).info(f"Browser '{browser_id}' has been added to the pool")
        return new_browser

    @pyd.validate_arguments
    @run_if_pool_accepts_new_jobs
    async def remove_browser_by_id(self, browser_id: str, force: bool = False) -> bool:
        "Remove browser from pool by its ID"
        if browser_id not in self._pool or not force and self._pool[browser_id].page_count > 0:
            return False

        browser = self._pool[browser_id]
        if browser and browser._browser:
            await browser.close()
        del self._pool[browser_id]
        logger.bind(pool_id=self.id_).info(f"Browser '{browser_id}' has been removed from the pool")
        return True

    @pyd.validate_arguments
    @run_if_pool_accepts_new_jobs
    def get_browser_by_id(self, browser_id: str) -> Optional[LeasedBrowser]:
        "Get browser by its ID"
        return self._pool.get(browser_id)

    @run_if_pool_accepts_new_jobs
    def get_least_busy_browser(self, create_if_none: bool) -> Optional[LeasedBrowser]:
        """
        Get the next available browser in the pool.
        If all browsers are full, raises an `NoAvailableBrowserError` exception.
        """
        if len(self.browsers) == 0:
            if create_if_none:
                return self.create_new_browser()
            return None

        elif len(self.browsers) == 1:
            return list(self._pool.values())[0]

        least_busy_browser_idx = 0
        for idx, browser in enumerate(self.browsers):
            if (
                not browser.is_idle
                and browser.page_count > 0
                and browser.page_count < self.browsers[least_busy_browser_idx].page_count
            ):
                least_busy_browser_idx = idx

        if browser := self.browsers[least_busy_browser_idx].has_capacity:
            return browser

        raise NoAvailableBrowserError(
            "All browsers are currently at full capacity! try again later."
        )

    def auto_scale_up(self) -> Optional[LeasedBrowser]:
        "Scale up the pool by creating a new browser instance"
        # Check if the total number of pages across all browsers is greater than 50% of current capacity
        total_page_cap = conf.browser_max_cached_items * len(self.browsers)
        total_active_pages = sum([browser.page_count for browser in self._pool.values()])
        avg_cpu_usage = sum(browser.monitor_browser[0] for browser in self.browsers) / len(
            self.browsers
        )
        if total_active_pages > 0 and (
            total_active_pages >= (total_page_cap * 0.6) or avg_cpu_usage >= 0.7
        ):
            try:
                self.create_new_browser()
                logger.bind(pool_id=self.id_, action="scale_up").info(
                    f"Scaled up to {len(self.browsers)} browsers"
                )

            except BrowserPoolCapacityReachedError as e:
                logger.bind(pool_id=self.id_, action="scale_up").warning(f"Scaling up failed: {e}")

    async def auto_scale_down(self) -> None:
        "Scale down the pool by removing the least busy browser instance"
        # Check if the total number of pages across all browsers is less than 25% of current capacity
        total_page_cap = conf.browser_max_cached_items * len(self.browsers)
        total_active_pages = sum([browser.page_count for browser in self._pool.values()])
        avg_cpu_usage = sum(browser.monitor_browser[0] for browser in self.browsers) / len(
            self.browsers
        )
        if total_active_pages <= (total_page_cap * 0.3) or avg_cpu_usage <= 0.3:
            candidates_for_deletion = [
                browser for browser in self.browsers if browser.page_count == 0 or browser.is_idle
            ]
            if len(candidates_for_deletion) > 0:
                [
                    await self.remove_browser_by_id(candidate.id_)
                    for candidate in candidates_for_deletion
                ]
                logger.bind(pool_id=self.id_, action="scale_down").info(
                    f"Scaled down to {len(self.browsers)} browsers"
                )
