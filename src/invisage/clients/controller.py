import pyppeteer
import atexit
import asyncio
import cachetools
import uuid
import pydantic as pyd

from contextlib import asynccontextmanager

import pyppeteer.page
from web_weaver.config import config as conf
from web_weaver.utils.metrics import log_execution_metrics
from web_weaver.logger import logger
from web_weaver.schemas.constants.page_action_type import PageActionType


CACHE = cachetools.TTLCache(maxsize=conf.max_cached, ttl=conf.cache_ttl)


class BrowserController:
    _browser = None

    @classmethod
    async def get_browser(cls):
        "Get the browser's instance; created a new browser if none in already running"
        if cls._browser is None:
            config = dict(
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
            )

            cls._browser = await pyppeteer.launch(**config)

            atexit.register(cls.close_browser)
        return cls._browser

    @classmethod
    @asynccontextmanager
    async def get_new_page(cls):
        browser = await cls.get_browser()
        new_page = await browser.newPage()
        try:
            yield new_page
        finally:
            await new_page.close()

    @classmethod
    def close_browser(cls) -> None:
        if cls._browser is not None:
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(cls._browser.close)
            cls._browser = None

    @classmethod
    async def start_page_session(cls, session_id: uuid.UUID) -> None:
        "Created a new pages and storing it in cache coupled with it's session ID"
        if CACHE.get(session_id):
            raise Exception("Page session already exists for this session_id.")
        browser = await cls.get_browser()
        new_page = await browser.newPage()
        CACHE[session_id] = new_page

    @classmethod
    async def retrieve_cached_page(cls, session_id: uuid.UUID) -> pyppeteer.page.Page:
        "Retrieves a page from cache memory"
        page: pyppeteer.page.Page = CACHE.get(session_id)
        if not page:
            raise KeyError(
                f"Page not found [page: '{session_id}'] - session has already been closed"
            )
        return page

    @classmethod
    async def remove_cached_page(cls, session_id: uuid.UUID) -> None:
        "Removes a cached page from memory - ending the session"
        page = await cls.retrieve_cached_page(session_id)
        try:
            await page.close()
        except Exception as e:
            raise
        finally:
            del CACHE[session_id]

    @classmethod
    @pyd.validate_arguments
    @log_execution_metrics
    async def extract_page_contents(cls, page: pyppeteer.page.Page) -> dict:
        return dict(
            url=page.url,
            title=await page.title(),
            content=await page.content(),
            cookies=await page.cookies(),
        )

    @classmethod
    @pyd.validate_arguments
    @log_execution_metrics
    async def fetch_page_contents(cls, url: str, **kwargs) -> dict:
        async with BrowserController.get_new_page() as page:
            logger.debug(f"Browser fetching URL='{url}'...")
            fetch_config = {
                "waitUntil": kwargs.pop("waitUntil", "domcontentloaded"),
                "timeout": kwargs.pop("timeout", 0),
            }
            wait_for_content = kwargs.pop("waitForContent", None)
            fetch_config.update(**kwargs)
            await page.goto(url, options=fetch_config)
            if wait_for_content:
                await cls._wait_until_contains(page, wait_for_content)
            logger.debug(f"Page loaded: URL='{url}'")
            return await cls.extract_page_contents(page)

    async def _wait_until_contains(
        page, text: str, timeout: int = 30000, interval: int = 500
    ) -> bool:
        elapsed = 0
        while elapsed < timeout:
            content = await page.content()
            if text in content:
                return True
            await asyncio.sleep(interval / 1000)
            elapsed += interval
        raise asyncio.TimeoutError(f"Timeout: Could not find '{text}' in the page content.")

    @classmethod
    @pyd.validate_arguments
    @log_execution_metrics
    async def page_action(cls, page: pyppeteer.page.Page, action: PageActionType, **kwargs) -> dict:
        match action:
            case PageActionType.CLICK:
                selector = kwargs.pop("selector")
                options = kwargs.pop("options", None)
                await page.waitForSelector(selector)
                await page.click(selector, options)
            case PageActionType.AUTHENTICATE:
                credentials = kwargs.pop("credentials")
                await page.authenticate(credentials)
            case PageActionType.SET_USER_AGENT:
                user_agent = kwargs.pop("user_agent")
                await page.setUserAgent(user_agent)
            case PageActionType.SCREENSHOT:
                options = kwargs.pop("options", None)
                await page.screenshot(options)
            case PageActionType.GOTO:
                url = kwargs.pop("url")
                options = kwargs.pop("options", None)
                await page.goto(url, options)
                if kwargs.get("waitForContent"):
                    await cls._wait_until_contains(page, kwargs.get("waitForContent"))
            case PageActionType.GO_BACK:
                options = kwargs.pop("options", None)
                await page.goBack(options)
            case PageActionType.GO_FORWARD:
                options = kwargs.pop("options", None)
                await page.goForward(options)

        return await cls.extract_page_contents(page)
