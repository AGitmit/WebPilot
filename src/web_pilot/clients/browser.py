import cachetools
import pyppeteer
import asyncio
import json
import uuid
import pydantic as pyd

from web_pilot.config import config as conf
from web_pilot.logger import logger
from contextlib import asynccontextmanager
from web_pilot.utils.ttl_cache import TTLCache


class Browser:
    id_: uuid.UUID
    browser: pyppeteer.browser.Browser
    pages: cachetools.TTLCache
    config: dict

    def __repr__(self) -> str:
        return f"Browser(id={self.id_}, page_count={self.page_count()}, config={self.config})"

    @pyd.validate_arguments
    def __init__(self, id_: uuid.UUID, config: dict = None) -> None:
        "Create Browser instance"
        self.id_ = id_
        self.pages = TTLCache()
        self.config = config or self._load_browser_config()
        asyncio.get_event_loop().run_until_complete(self._instantiate_browser())

    def _load_browser_config(self) -> dict:
        config = self._get_default_config()
        try:
            config.update(json.loads(open(conf.browser_config_file).read()))
        except FileNotFoundError:
            logger.info(
                "'default_browser_config.json' file not found - using default configurations"
            )
        except Exception as e:
            logger.error(f"{str(e)} - using default configurations")
        return config

    @staticmethod
    def _get_default_config() -> dict:
        return {
            "headless": conf.browser_headless,
            "autoClose": conf.browser_auto_close,
            "args": [
                "--disable-web-security",
                "--host-resolver-rules=MAP localhost 127.0.0.1",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
            "executablePath": conf.chromium_path,
        }

    async def _instantiate_browser(self) -> pyppeteer.browser.Browser:
        "Create Pyppeteer browser instance"

        async def create():
            self.browser = await pyppeteer.launch(**self.config)

        await create()

    def page_count(self) -> int:
        return len(self.pages)

    async def close(self) -> None:
        await self.browser.close()

    @asynccontextmanager
    async def _get_new_page(self):
        new_page = await self.browser.newPage()
        try:
            yield new_page
        except Exception as e:
            logger.error(e)
        finally:
            await new_page.close()

    async def start_remote_page_session(self) -> uuid.UUID:
        "Created new page and store it in cache by it's session-ID"
        session_id = uuid.uuid4().__str__()
        new_page = await self.browser.newPage()
        self.pages[session_id] = new_page
        logger.bind(browser_id=self.id_).info(
            f"Created new page session: '{session_id}' successfully"
        )
        return session_id

    async def retrieve_page_session(self, session_id: uuid.UUID) -> pyppeteer.page.Page:
        "Retrieves a page-session from cache memory"
        page: pyppeteer.page.Page = self.browser.pages.pop(session_id)
        if not page:
            raise KeyError(
                f"Page not found [page: '{session_id}'] - session has already been closed!"
            )
        return page

    async def close_page_session(self, session_id: uuid.UUID) -> None:
        "Closes and removes a cached page-session from memory - ending the session"
        page = await self.retrieve_page_session(session_id)
        try:
            await page.close()
        except Exception as e:
            logger.bind(browser_id=self.id_, session_id=session_id).error(e)
            raise
        finally:
            logger.bind(browser_id=self.id_, session_id=session_id).info(
                "Page session closed successfully"
            )
            del self.browser.pages[session_id]
