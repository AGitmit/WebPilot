import pyppeteer
import asyncio
import uuid
import pydantic as pyd
import json

from contextlib import asynccontextmanager

from web_pilot.utils.metrics import log_execution_metrics
from web_pilot.logger import logger
from web_pilot.schemas.constants.page_action_type import PageActionType
from web_pilot.clients.browser import LeasedBrowser


class BrowserController:
    @classmethod
    @asynccontextmanager
    async def get_new_page(cls, browser: LeasedBrowser):
        new_page = await browser.browser.newPage()
        try:
            yield new_page
        finally:
            await new_page.close()

    @classmethod
    async def start_remote_page_session(cls, browser: LeasedBrowser) -> uuid.UUID:
        "Created new page and store it in cache by it's session-ID"
        session_id = uuid.uuid4().__str__()
        new_page = await browser.browser.newPage()
        browser.pages[session_id] = new_page
        return session_id

    @classmethod
    async def retrieve_page_session(
        cls, browser: LeasedBrowser, session_id: uuid.UUID
    ) -> pyppeteer.page.Page:
        "Retrieves a page-session from cache memory"
        page: pyppeteer.page.Page = browser.pages.get(session_id)
        if not page:
            raise KeyError(
                f"Page not found [page: '{session_id}'] - session has already been closed!"
            )
        return page

    @classmethod
    async def close_remove_page_session(cls, browser: LeasedBrowser, session_id: uuid.UUID) -> None:
        "Removes a cached page-session from memory - ending the session"
        page = await cls.retrieve_page_session(session_id)
        try:
            await page.close()
        except Exception as e:
            raise
        finally:
            del browser.pages[session_id]

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

    async def save_session_snapshot(page) -> dict:
        cookies = await page.cookies()
        local_storage = await page.evaluate(
            "JSON.stringify(Object.assign({}, window.localStorage))"
        )
        session_storage = await page.evaluate(
            "JSON.stringify(Object.assign({}, window.sessionStorage))"
        )
        url = page.url

        snapshot = {
            "cookies": cookies,
            "local_storage": local_storage,
            "session_storage": session_storage,
            "url": url,
        }
        return snapshot

    @classmethod
    async def restore_session_snapshot(cls, snapshot: dict) -> pyppeteer.page.Page:
        browser = await cls.get_browser()
        page = await browser.newPage()

        # Set cookies
        await page.setCookie(*snapshot["cookies"])

        # Navigate to a minimal valid page to access storage APIs
        await page.goto("http://www.google.com")

        # Restore local storage and session storage
        await page.evaluate(
            f"""
            Object.assign(window.localStorage, JSON.parse({json.dumps(snapshot['local_storage'])}));
            Object.assign(window.sessionStorage, JSON.parse({json.dumps(snapshot['session_storage'])}));
        """
        )

        # Navigate to the saved URL
        await page.goto(snapshot["url"])
        return page

    @classmethod
    @pyd.validate_arguments
    @log_execution_metrics
    async def page_action(cls, page: pyppeteer.page.Page, action: PageActionType, **kwargs) -> dict:
        global snapshot
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
            case PageActionType.SAVE_SNAPSHOT:
                snapshot = await cls.save_session_snapshot(page)
            case PageActionType.RESTORE_SNAPSHOT:
                page = await cls.restore_session_snapshot(snapshot)

        return await cls.extract_page_contents(page)
