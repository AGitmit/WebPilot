import pydantic as pyd
import uuid
import json

from pyppeteer import page
from web_pilot.config import config as conf
from web_pilot.utils.page_util import PageUtil
from web_pilot.schemas.pages import Snapshot, PageContent


__all__ = ["Page", "Snapshot", "PageContent"]


class Page(page.Page):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._pyppeteer_page = self
        self.session_id: uuid.UUID = uuid.uuid4()
        self.parent_browser: int = kwargs.get("browser_id", None)

    @property
    def pyppeteer_page(self) -> page.Page:
        return self._pyppeteer_page

    @pyd.validate_arguments
    async def click(
        self, selector: str, options: dict = None, wait_for_selector: bool = True
    ) -> None:
        if wait_for_selector:
            await page.waitForSelector(selector)
        await self._pyppeteer_page.click(selector, options)

    async def wait_for_content(self, content: str) -> None:
        await PageUtil._wait_until_contains(self._pyppeteer_page, content)

    @pyd.validate_arguments
    async def save_snapshot(self) -> Snapshot:
        cookies = await self.cookies()
        local_storage = await self.evaluate(
            "JSON.stringify(Object.assign({}, window.localStorage))"
        )
        session_storage = await self.evaluate(
            "JSON.stringify(Object.assign({}, window.sessionStorage))"
        )
        url = self.url

        return Snapshot(
            url=url, cookies=cookies, local_storage=local_storage, session_storage=session_storage
        )

    async def restore_from_snapshot(self, snapshot: Snapshot) -> None:
        # Set cookies
        await self.setCookie(*snapshot.cookies)

        # Navigate to a minimal valid page to access storage APIs
        await self.goto(f"http://{conf.host_address}:{conf.host_port}")

        # Restore local storage and session storage
        await self.evaluate(
            f"""
            Object.assign(window.localStorage, JSON.parse({json.dumps(snapshot.local_storage)}));
            Object.assign(window.sessionStorage, JSON.parse({json.dumps(snapshot.session_storage)}));
        """
        )

    async def extract_page_contents(self) -> PageContent:
        return PageContent(
            url=self.url,
            title=await self.title(),
            content=await self.content(),
        )
