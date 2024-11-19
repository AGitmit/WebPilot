import pyppeteer
import psutil
import pydantic as pyd
import pyppeteer.browser
import pyppeteer.launcher

from typing import Optional
from web_pilot.config import config as conf
from web_pilot.logger import logger
from web_pilot.utils.ttl_cache import TTLCache
from web_pilot.clients.page_session import PageSession
from web_pilot.utils.fake_ua import fake_user_agent, Platform, BrowserTypes
from web_pilot.exc import FailedToLaunchBrowser


class LeasedBrowser:
    id_: str
    _browser: pyppeteer.browser.Browser
    pages: TTLCache
    platform: Platform
    browser_type: BrowserTypes
    _parent: str

    @pyd.validate_arguments
    def __init__(
        self,
        id_: str,
        parent: str,
        headless: bool = True,
        incognito: bool = False,
        gpu: bool = False,
        privacy: bool = False,
        ignore_http_errors: bool = True,
        spa_mode: bool = False,
        proxy_server: Optional[str] = None,
        platform: Optional[Platform] = None,
        browser: Optional[BrowserTypes] = None,
    ) -> None:
        "Create Browser instance"
        self.id_ = id_
        self._browser = None
        self._parent = parent
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

    def __repr__(self) -> dict:
        return dict(
            id=self.id_,
            page_count=self.page_count,
            platform=self.platform.value,
            browser=self.browser_type.value,
            is_idle=self.is_idle,
        )

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
                f"--host-resolver-rules=MAP localhost {conf.host_address}",
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
        try:
            self._browser = await pyppeteer.launch(**self.config)

        except pyppeteer.errors.PuppeteerError as e:
            logger.bind(browser_id=self.id_).error(f"Failed to launch browser: {e}", exc_info=True)
            raise FailedToLaunchBrowser(e)

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def pid(self) -> int:
        process = self._browser.process
        return process.pid

    @property
    def monitor_browser(self) -> tuple[float, float]:
        """Monitor the resource usage of a browser process."""
        try:
            process = psutil.Process(self.pid)
            cpu_usage = (
                process.cpu_percent(interval=0.1) / psutil.cpu_count()
            )  # CPU usage of the process
            memory_usage = process.memory_info().rss / (1024 * 1024)  # Memory in MB
            return cpu_usage, memory_usage

        except psutil.NoSuchProcess:
            return 0, 0

    @property
    def is_idle(self) -> bool:
        return all([page.is_idle for page in self.pages._cache.values()])

    @property
    def has_capacity(self) -> bool:
        return self.page_count < conf.max_cached_items

    async def close(self) -> None:
        await self._browser.close()

    async def start_page_session(self, session_id_prefix: str) -> str:
        "Created new page and store it in cache by it's session-ID"
        if not self._browser:
            await self._instantiate_browser()

        page_id = len(self.pages)
        new_page_session = PageSession(page_obj=await self._browser.newPage(), page_id=page_id)
        self.pages.set_item(page_id, new_page_session)
        session_id = f"{session_id_prefix}_{str(page_id)}"
        logger.bind(browser_id=self.id_).info(
            f"Created new page session: '{session_id}' successfully"
        )
        return session_id

    def pop_page_session(self, page_id: int) -> PageSession:
        "Retrieves a page-session from cache memory"
        page_session: PageSession = self.pages.pop_item(page_id)
        if page_session:
            return page_session
        raise KeyError(f"Page not found [page: '{page_id}'] - session has already been closed!")

    def get_page_session(self, page_id: int) -> PageSession:
        "Retrieves a page-session from cache memory"
        page_session: PageSession = self.pages.get_item(page_id)
        if page_session:
            return page_session
        raise KeyError(f"Page not found [page: '{page_id}'] - session has already been closed!")

    def put_page_session(self, page_id: int, page: PageSession) -> None:
        "Puts a page-session back to cache memory - resetting the TTL"
        self.pages.set_item(page_id, page)

    async def close_page_session(self, page_id: int) -> None:
        "Closes and removes a cached page-session from memory - ending the session"
        page_session = self.pop_page_session(page_id)
        try:
            await page_session._page.close()
        except Exception as e:
            logger.bind(browser_id=self.id_, session_id=page_id).error(e)
            raise
        finally:
            logger.bind(browser_id=self.id_, session_id=page_id).info(
                "Page session closed successfully"
            )
            self.pages.delete_item(page_id)  # maybe uneccessary right now since we use pop_item()
