import asyncio
import pydantic as pyd

from invisage.clients.page import Page, Snapshot, PageContent
from invisage.schemas.constants.page_action_type import PageActionType
from invisage.utils.metrics import log_execution_metrics, logger
from invisage.exc import UnableToPerformActionError
from typing import Union


class PageUtil:
    @staticmethod
    async def _wait_until_contains(
        page: Page, text: str, timeout: int = 30000, interval: int = 500
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
    async def perform_page_action(
        cls, page: Page, action: PageActionType, **kwargs
    ) -> Union[PageContent, Snapshot]:
        try:
            match action:
                case PageActionType.CLICK:
                    if selector := kwargs.pop("selector", None) is None:
                        raise ValueError(
                            f"Selector is required for {PageActionType.CLICK.value} action"
                        )
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
                    return await page.save_snapshot(page)

                case PageActionType.RESTORE_SNAPSHOT:
                    page = await page.restore_from_snapshot(snapshot)

            return await page.extract_page_contents(page)
        except Exception as e:
            logger.bind(
                browser_id=page.parent_browser, session_id=str(page.session_id), page_action=action
            ).error(f"Unable to perform action - {e}")
            raise UnableToPerformActionError(e)