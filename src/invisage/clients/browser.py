import cachetools
import pyppeteer
import asyncio

from invisage.config import config as conf
from invisage.logger import logger

__all__ = ["Browser"]


class Browser:
    id_: int
    browser: pyppeteer.browser.Browser
    page_count: int
    cache: cachetools.TTLCache
    config: dict

    def __init__(self, id_: int) -> None:
        "Create Browser instance"
        self._check_chromium()

        self.id_ = id_
        self.page_count = 0
        self.cache = cachetools.TTLCache(maxsize=conf.page_cache_cap, ttl=conf.page_cache_ttl)
        self.config = dict(
            headless=True,
            autoClose=False,
            args=[
                "--disable-web-security",
                "--host-resolver-rules=MAP localhost 127.0.0.1",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
            executablePath=conf.chromium_path,
        )  # TODO: research more deeply on the browser options
        self._instantiate_browser()

    def _check_chromium(self):
        if not pyppeteer.chromium_downloader.check_chromium():
            logger.info("Downloading Chromium...")
            pyppeteer.chromium_downloader.download_chromium()
            logger.info("Chromium downloaded successfully")
        
    def _instantiate_browser(self) -> pyppeteer.browser.Browser:
        "Create Pyppeteer browser instance"

        async def create():
            self.browser = await pyppeteer.launch(**self.config)

        asyncio.get_event_loop().run_until_complete(create())