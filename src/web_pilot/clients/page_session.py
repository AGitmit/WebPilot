import pydantic as pyd
import uuid
import json
import asyncio
import pyppeteer

from web_pilot.config import config as conf
from web_pilot.schemas.pages import Snapshot, PageContent


class PageSession:
    page: pyppeteer.page.Page
    session_id: uuid.UUID
    parent: uuid.UUID

    def __init__(self, page: pyppeteer.page.Page, **kwargs) -> None:
        self.page = page
        self.session_id = uuid.uuid4()
        self.parent = kwargs.get("parent", None)

    def __repr__(self) -> str:
        return f"Page(id={self.session_id.__str__()}, parent={self.parent.__str__()})"

    @property
    def page(self) -> pyppeteer.page.Page:
        return self.page

    @pyd.validate_arguments
    async def click(
        self, selector: str, options: dict = None, wait_for_selector: bool = True
    ) -> None:
        if wait_for_selector:
            await self.page.waitForSelector(selector)
        await self.page.click(selector, options)

    async def wait_for_content(self, content: str) -> None:
        await self._wait_until_contains(content)

    @pyd.validate_arguments
    async def save_snapshot(self) -> Snapshot:
        # TODO: replace with the new method of saving snapshot
        cookies = await self.page.cookies()
        local_storage = await self.page.evaluate(
            "JSON.stringify(Object.assign({}, window.localStorage))"
        )
        session_storage = await self.page.evaluate(
            "JSON.stringify(Object.assign({}, window.sessionStorage))"
        )
        url = self.page.url

        return Snapshot(
            url=url, cookies=cookies, local_storage=local_storage, session_storage=session_storage
        )

    async def restore_from_snapshot(self, snapshot: Snapshot) -> None:
        # TODO: replace with the new method of restoring snapshot
        # Set cookies
        await self.page.setCookie(*snapshot.cookies)

        # Navigate to a minimal valid page to access storage APIs
        await self.page.goto(f"http://{conf.host_address}:{conf.host_port}")

        # Restore local storage and session storage
        await self.page.evaluate(
            f"""
            Object.assign(window.localStorage, JSON.parse({json.dumps(snapshot.local_storage)}));
            Object.assign(window.sessionStorage, JSON.parse({json.dumps(snapshot.session_storage)}));
        """
        )

    async def extract_page_contents(self) -> PageContent:
        return PageContent(
            url=self.page.url,
            title=await self.page.title(),
            content=await self.page.content(),
        )

    async def _wait_until_contains(
        self, text: str, timeout: int = 30000, interval: int = 500
    ) -> bool:
        elapsed = 0
        while elapsed < timeout:
            content = await self.page.content()
            if text in content:
                return True
            await asyncio.sleep(interval / 1000)
            elapsed += interval
        raise asyncio.TimeoutError(f"Timeout: Could not find '{text}' in the page content.")

    # async def usage_metrics(self):
    #     # gather and view usage of resources for current visited host
    #     # Create a single CDP session
    #     cdp_client = await self.page.target.createCDPSession()
    #     metrics = await cdp_client.send("Performance.getMetrics")
    #     storage = await cdp_client.send("Storage.getUsageAndQuota", {
    #     "origin": self.page.url
    #     })

    # @pyd.validate_arguments
    # @log_execution_metrics
    # async def perform_page_action(
    #    self, action: PageActionType, **kwargs
    # ) -> Union[PageContent, Snapshot]:
    #     global SNAPSHOT  # only for testing
    #     try:
    #         match action:
    #             case PageActionType.CLICK:
    #                 if selector := kwargs.pop("selector", None) is None:
    #                     raise ValueError(
    #                         f"Selector is required for {PageActionType.CLICK.value} action"
    #                     )
    #                 options = kwargs.pop("options", None)
    #                 await page.waitForSelector(selector)
    #                 await page.click(selector, options)

    #             case PageActionType.AUTHENTICATE:
    #                 credentials = kwargs.pop("credentials")
    #                 await page.authenticate(credentials)

    #             case PageActionType.SET_USER_AGENT:
    #                 user_agent = kwargs.pop("user_agent")
    #                 await page.setUserAgent(user_agent)

    #             case PageActionType.SCREENSHOT:
    #                 options = kwargs.pop("options", None)
    #                 await page.screenshot(options)

    #             case PageActionType.GOTO:
    #                 url = kwargs.pop("url")
    #                 options = kwargs.pop("options", None)
    #                 await page.goto(url, options)
    #                 if kwargs.get("waitForContent"):
    #                     await cls._wait_until_contains(page, kwargs.get("waitForContent"))

    #             case PageActionType.GO_BACK:
    #                 options = kwargs.pop("options", None)
    #                 await page.goBack(options)

    #             case PageActionType.GO_FORWARD:
    #                 options = kwargs.pop("options", None)
    #                 await page.goForward(options)

    #             case PageActionType.SAVE_SNAPSHOT:
    #                 SNAPSHOT = await page.save_snapshot(page)

    #             case PageActionType.RESTORE_SNAPSHOT:
    #                 page = await page.restore_from_snapshot(SNAPSHOT)

    #             case PageActionType.EVALUATE:
    #                 code = kwargs.pop("code")
    #                 args = kwargs.pop("args", [])
    #                 await page.evaluate(code, *args)

    #         return await page.extract_page_contents(page)

    #     except Exception as e:
    #         logger.bind(
    #             browser_id=page.parent_browser, session_id=str(page.session_id), page_action=action
    #         ).error(f"Unable to perform action - {e}")
    #         raise UnableToPerformActionError(e)
