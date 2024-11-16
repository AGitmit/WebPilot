import pydantic as pyd
import pyppeteer
import asyncio

from web_pilot.exc import InvalidSessionIDError
from web_pilot.utils.snapshot_util import SnapshotUtil
from web_pilot.schemas.pages import Snapshot, PageContent
from typing import Type


# Utils
@pyd.validate_arguments
def break_session_id_to_parts(session_id: str) -> tuple:
    try:
        pool_id, browser_id, page_id = session_id.split("_")
        return (pool_id, browser_id, page_id)

    except ValueError:
        raise InvalidSessionIDError("Invalid session ID")


# Page actions
@pyd.validate_arguments
async def _wait_for_text(self, text: str, timeout: int = 30000, interval: int = 500) -> bool:
    elapsed = 0
    while elapsed < timeout:
        content = await self._page.content()
        if text in content:
            return True
        await asyncio.sleep(interval / 1000)
        elapsed += interval
    raise asyncio.TimeoutError(f"Timeout: Could not find '{text}' in the page content.")


@pyd.validate_arguments
async def perform_action_click(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    if selector := kwargs.pop("selector", None) is None:
        raise ValueError(f"Selector is required for 'click' action")

    wait_for_selector = kwargs.pop("waitForSelector", True)
    options = kwargs.pop("options", None)
    if wait_for_selector:
        await page.waitForSelector(selector)
    await page.click(selector, options)


@pyd.validate_arguments
async def perform_action_authenticate(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    credentials = kwargs.pop("credentials")
    await page.authenticate(credentials)


@pyd.validate_arguments
async def perform_action_setUserAgent(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    user_agent = kwargs.pop("user_agent")
    await page.setUserAgent(user_agent)


@pyd.validate_arguments
async def perform_action_screenshot(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    options = kwargs.pop("options", None)
    await page.screenshot(options)


@pyd.validate_arguments
async def perform_action_goto(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    url = kwargs.pop("url", None)
    if not url:
        raise ValueError("URL is required for 'goto' action")

    options = kwargs.pop("options", None)
    await page.goto(url, options)
    if kwargs.get("waitForText"):
        await _wait_for_text(kwargs.get("waitForText"))


@pyd.validate_arguments
async def perform_action_goBack(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    options = kwargs.pop("options", None)
    await page.goBack(options)


@pyd.validate_arguments
async def perform_action_goForward(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    options = kwargs.pop("options", None)
    await page.goForward(options)


@pyd.validate_arguments
async def perform_action_saveSnapshot(page: Type[pyppeteer.page.Page]) -> Snapshot:
    return await SnapshotUtil.capture_session_snapshot(page)


@pyd.validate_arguments
async def perform_action_restoreSnapshot(
    page: Type[pyppeteer.page.Page], snapshot: Snapshot
) -> None:
    await SnapshotUtil.restore_session(page, snapshot)


@pyd.validate_arguments
async def perform_action_setViewport(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    width = kwargs.pop("width")
    height = kwargs.pop("height")
    await page.setViewport({"width": width, "height": height})


@pyd.validate_arguments
async def perform_action_setCookie(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    cookies = kwargs.pop("cookies")
    await page.setCookie(*cookies)


@pyd.validate_arguments
async def perform_action_deleteCookie(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    cookies = kwargs.pop("cookies", None)
    all_ = kwargs.pop("all", False)
    if all_:
        await page.deleteCookies()
    else:
        await page.deleteCookie(*cookies)


@pyd.validate_arguments
async def perform_action_evaluate(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    code = kwargs.pop("code")
    args = kwargs.pop("args", [])
    return await page.evaluate(code, *args)


@pyd.validate_arguments
async def perform_action_evaluateOnNewDocument(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    code = kwargs.pop("code")
    args = kwargs.pop("args", [])
    return await page.evaluateOnNewDocument(code, *args)


@pyd.validate_arguments
async def perform_action_evaluateHandle(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    code = kwargs.pop("code")
    args = kwargs.pop("args", [])
    return await page.evaluateHandle(code, *args)


@pyd.validate_arguments
async def perform_action_addScriptTag(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    url = kwargs.pop("url")
    return await page.addScriptTag(url=url)


@pyd.validate_arguments
async def perform_action_removeScriptTag(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    handle = kwargs.pop("handle")
    return await page.removeScriptTag(handle)


@pyd.validate_arguments
async def perform_action_exposeFunction(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    name = kwargs.pop("name")
    code = kwargs.pop("code")
    return await page.exposeFunction(name, code)


@pyd.validate_arguments
async def perform_action_removeFunction(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    name = kwargs.pop("name")
    return await page.removeFunction(name)


@pyd.validate_arguments
async def perform_action_extractPageContents(page: Type[pyppeteer.page.Page]) -> PageContent:
    return PageContent(
        url=page.url,
        title=await page.title(),
        content=await page.content(),
    )


@pyd.validate_arguments
async def perform_action_setGeoLocation(page: Type[pyppeteer.page.Page], **kwargs) -> None:
    latitude = kwargs.pop("latitude")
    longitude = kwargs.pop("longitude")
    await page.setGeolocation({"latitude": latitude, "longitude": longitude})


@pyd.validate_arguments
async def perform_action_clearGeolocation(page: Type[pyppeteer.page.Page]) -> None:
    await page.setGeolocation(None)
