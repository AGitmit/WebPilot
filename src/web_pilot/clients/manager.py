import pyppeteer
import uuid
import pydantic as pyd

from typing import Optional
from web_pilot.config import config as conf
from web_pilot.clients.browser import Browser
from web_pilot.exc import BrowserPoolCapacityReachedError, NoAvailableBrowserError


class BrowserManager:
    _pool: dict = {}
    max_browsers: int = conf.max_browsers_cap
    rr_current_index: int = 0
    auto_scale_browsers: bool = conf.auto_scale

    @property
    def browsers(cls) -> list[Browser]:
        return list(cls._pool.values())

    @classmethod
    @pyd.validate_arguments
    def create_new_browser(cls, config: Optional[dict] = None) -> str:
        "Create and return a new browser instance"
        browser_id = uuid.uuid4().__str__()
        if len(cls._pool) >= cls.max_browsers:
            raise BrowserPoolCapacityReachedError(
                f"Max number of browsers in pool reached: {cls.max_browsers}"
            )
        cls._pool[browser_id] = Browser(browser_id, config)
        return browser_id

    @classmethod
    @pyd.validate_arguments
    def remove_browser_by_id(cls, browser_id: uuid.UUID, force: bool = False) -> bool:
        "Remove browser from pool by its ID"
        if browser_id not in cls._pool or not force and cls._pool[browser_id].page_count() > 0:
            return False

        cls._pool[browser_id].browser.close()
        del cls._pool[browser_id]
        return True

    @classmethod
    @pyd.validate_arguments
    def get_browser_by_id(cls, browser_id: uuid.UUID) -> Optional[pyppeteer.browser.Browser]:
        "Get browser by its ID"
        return cls._pool.get(browser_id)

    @classmethod
    async def get_next_browser(cls) -> pyppeteer.browser.Browser:
        """
        Get the next available browser in the pool - round-robin.
        If all browsers are full, raises an `NoAvailableBrowserError` exception.
        This method is used if `balance_load` is set to `True`.
        """

        if cls.auto_scale_browsers:
            if len(cls._pool) < cls.max_browsers:
                return cls.create_new_browser()

        for _ in range(len(cls.browsers)):
            browser: Browser = cls.browsers[cls.rr_current_index]
            # Check if browser has capacity for more pages
            if browser.page_count < conf.max_cached_items:
                cls.rr_current_index = (cls.rr_current_index + 1) % len(cls.browsers)
                return browser
            # Move to the next browser
            cls.rr_current_index = (cls.rr_current_index + 1) % len(cls.browsers)

        # If all browsers are full, raise an exception
        # TODO: implement optional wait logic
        raise NoAvailableBrowserError("All browsers are currently at capacity.")

    @classmethod
    def scale_up(cls):
        if cls.auto_scale_browsers:
            if len(cls._pool) < cls.max_browsers:
                return cls.create_new_browser()
