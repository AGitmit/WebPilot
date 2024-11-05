import pyppeteer

from typing import Optional
from web_weaver.config import config as conf
from web_weaver.clients.browser import Browser
from web_weaver.exc import BrowserPoolCapacityReachedError

__all__ = ["BrowserManager"]


class BrowserManager:
    def __init__(self):
        self._check_chromium()
        self._pool = {}
        self.max_browsers = conf.max_browsers_cap

    def _check_chromium(self):
        if not pyppeteer.chromium_downloader.check_chromium():
            pyppeteer.chromium_downloader.download_chromium()

    def get_browser(self, browser_id: int) -> Optional[pyppeteer.browser.Browser]:
        return self._pool.get(browser_id)

    async def create_browser(self) -> pyppeteer.browser.Browser:
        if len(self._pool) >= self.max_browsers:
            raise BrowserPoolCapacityReachedError(
                f"Max number of browsers in pool reached: {self.max_browsers}"
            )

        self._pool[len(self._pool)] = Browser(len(self._pool))
        return self._pool[len(self._pool)]
