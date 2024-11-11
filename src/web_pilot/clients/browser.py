import cachetools
import pyppeteer
import asyncio
import uuid
import pydantic as pyd
import pyppeteer.browser
import pyppeteer.launcher

from typing import Optional
from web_pilot.config import config as conf
from web_pilot.logger import logger
from web_pilot.utils.ttl_cache import TTLCache
from web_pilot.clients.page_session import PageSession
from web_pilot.utils.fake_ua import fake_user_agent, Platform, BrowserTypes


class LeasedBrowser:
    id_: uuid.UUID
    _browser: pyppeteer.browser.Browser
    pages: TTLCache
    platform: Platform
    browser_type: BrowserTypes

    @pyd.validate_arguments
    def __init__(
        self,
        id_: uuid.UUID,
        headless: bool = True,
        incognito: bool = False,
        gpu: bool = False,
        privacy: bool = False,
        ignore_http_errors: bool = True,
        spa_mode: bool = False,
        proxy_server: Optional[str] = None,
        platform: Optional[Platform] = Platform.LINUX64,
        browser: Optional[BrowserTypes] = BrowserTypes.FIREFOX,
    ) -> None:
        "Create Browser instance"
        self.id_ = id_
        self.pages = TTLCache()
        self.config = self._load_browser_config(
            headless,
            incognito,
            gpu,
            privacy,
            ignore_http_errors,
            spa_mode,
            proxy_server,
            platform,
            browser,
        )
        self.platform = platform
        self.browser_type = browser
        asyncio.get_event_loop().run_until_complete(self._instantiate_browser())

    @property
    def id(self) -> uuid.UUID:
        return self.id_

    def __repr__(self) -> str:
        return f"Browser(id={self.id_.__str__()}, page_count={self.page_count()}, platform={self.platform.value}, browser={self.browser_type.value})"

    def _load_browser_config(
        self,
        headless: bool,
        incognito: bool,
        disable_gpu: bool,
        privacy: bool,
        ignore_http_errors: bool,
        spa_mode: bool,
        proxy_server: Optional[str],
        platform: Optional[Platform],
        browser: Optional[BrowserTypes],
    ) -> dict:
        config = {
            "headless": True if headless else False,
            "autoClose": False,
            "userDataDir": conf.user_data_dir,
            "executablePath": conf.chromium_path,
            "args": [
                "--host-resolver-rules=MAP localhost 127.0.0.1",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        }
        if incognito:
            config["args"].append("--incognito")
        if disable_gpu:
            config["args"].append("--disable-gpu")
        if privacy:
            config["args"].append("--disable-web-security")
            config["args"].append("--disable-features=IsolateOrigins,site-per-process")
            config["args"].append("--no-referrers")
        if ignore_http_errors:
            config["ignoreHTTPSErrors"] = True
        if spa_mode:
            config["args"].append("--single-process")
            config["args"].append("--disable-background-networking")
            config["args"].append("--disable-background-timer-throttling")
        if proxy_server:
            config["args"].append(f"--proxy-server={proxy_server}")
        if browser:
            config["args"].append(f"--user-agent={fake_user_agent(type=browser)}")
        if platform:
            config["args"].append(f"--platform={platform}")
        return config

    async def _instantiate_browser(self) -> None:
        "Create Pyppeteer browser instance"
        self._browser = await pyppeteer.launch(**self.config)

    def page_count(self) -> int:
        return self.pages.len()

    async def close(self) -> None:
        await self._browser.close()

    async def start_remote_page_session(self) -> uuid.UUID:
        "Created new page and store it in cache by it's session-ID"
        session_id = uuid.uuid4().__str__()
        new_page_session = PageSession(page=await self._browser.newPage(), parent=self.id_)
        self.pages.set_item(session_id, new_page_session)
        logger.bind(browser_id=self.id_).info(
            f"Created new page session: '{session_id}' successfully"
        )
        return session_id

    def retrieve_page_session(self, session_id: uuid.UUID) -> PageSession:
        "Retrieves a page-session from cache memory"
        page_session: PageSession = self.pages.get_item(session_id)
        if page_session:
            return page_session
        raise KeyError(f"Page not found [page: '{session_id}'] - session has already been closed!")

    async def close_page_session(self, session_id: uuid.UUID) -> None:
        "Closes and removes a cached page-session from memory - ending the session"
        page_session = self.retrieve_page_session(session_id)
        try:
            await page_session.page.close()
        except Exception as e:
            logger.bind(browser_id=self.id_, session_id=session_id).error(e)
            raise
        finally:
            logger.bind(browser_id=self.id_, session_id=session_id).info(
                "Page session closed successfully"
            )
            del self.pages.delete_item(session_id)
