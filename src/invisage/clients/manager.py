import pyppeteer

from typing import Optional
from invisage.config import config as conf
from invisage.clients.browser import Browser
from invisage.exc import BrowserPoolCapacityReachedError, NoAvailableBrowserError

__all__ = ["BrowserManager"]


class BrowserManager:
    def __init__(self):
        self._check_chromium()
        self._pool = {}
        self.max_browsers = conf.max_browsers_cap
        self.rr_current_index = 0

    def create_new_browser(self) -> pyppeteer.browser.Browser:
        "Create and return a new browser instance"
        if len(self._pool) >= self.max_browsers:
            raise BrowserPoolCapacityReachedError(
                f"Max number of browsers in pool reached: {self.max_browsers}"
            )
        browser_idx = len(self._pool) + 1
        self._pool[browser_idx] = Browser(browser_idx)
        return self._pool[len(self._pool)]

    def remove_browser_by_id(self, browser_id: int) -> None:
        "Remove browser from pool by its ID"
        if browser_id not in self._pool:
            return
        self._pool[browser_id].browser.close()
        del self._pool[browser_id]

    def get_browser_by_id(self, browser_id: int) -> Optional[pyppeteer.browser.Browser]:
        "Get browser by its ID"
        return self._pool.get(browser_id)

    async def get_next_browser(self) -> pyppeteer.browser.Browser:
        "Get the next available browser in the pool"

        if len(self._pool) < self.max_browsers:
            return self.create_new_browser()

        for _ in range(len(self.browsers)):
            browser: Browser = self.browsers[self.rr_current_index]
            # Check if browser has capacity for more pages
            if browser.page_count < conf.browser_pages_cap:
                self.rr_current_index = (self.rr_current_index + 1) % len(self.browsers)
                return browser
            # Move to the next browser
            self.rr_current_index = (self.rr_current_index + 1) % len(self.browsers)

        # If all browsers are full, raise an exception
        # TODO: implement optional wait logic
        raise NoAvailableBrowserError("All browsers are currently at capacity.")
