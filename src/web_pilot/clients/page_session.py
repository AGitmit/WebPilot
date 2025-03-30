import pydantic as pyd
import pyppeteer
import asyncio

from datetime import datetime, timedelta
from typing import Any, Optional
from web_pilot.schemas.constants.page_action_type import PageActionType
from web_pilot.logger import logger
from web_pilot.utils.decorators import log_elapsed_time
from web_pilot.exc import UnableToPerformActionError
from web_pilot.config import config as conf
from web_pilot.utils.sessions import (
    perform_action_click,
    perform_action_authenticate,
    perform_action_setUserAgent,
    perform_action_screenshot,
    perform_action_goto,
    perform_action_goBack,
    perform_action_goForward,
    perform_action_evaluate,
    perform_action_extractPageContents,
    perform_action_exposeFunction,
    perform_action_removeFunction,
    perform_action_setViewport,
    perform_action_evaluateOnNewDocument,
    perform_action_setCookie,
    perform_action_deleteCookie,
    perform_action_evaluateHandle,
    perform_action_addScriptTag,
    perform_action_removeScriptTag,
    perform_action_setGeoLocation,
    perform_action_clearGeolocation,
    perform_action_emulateMedia,
    perform_action_getAccessibilityTree,
    perform_action_setContent,
    perform_action_startJSCoverage,
    perform_action_stopJSCoverage,
    perform_action_setExtraHttpHeaders,
)


class PageSession:
    _page: pyppeteer.page.Page
    id_: str
    _last_used: Optional[datetime]

    def __init__(self, page_obj: pyppeteer.page.Page, page_id: int, **kwargs) -> None:
        self._page = page_obj
        self.id_ = page_id
        self._last_used = datetime.now()

    def __repr__(self) -> dict:
        return dict(
            id=self.id_,
            is_idle=self.is_idle,
            last_used=self._last_used,
            parent=self.id_.split("_")[0:2],
        )

    def __del__(self):
        # Schedule the cleanup asynchronously when the object is deleted (garbage collected)
        asyncio.ensure_future(self.cleanup())

    async def cleanup(self) -> None:
        try:
            await self._page.close()
            logger.bind(page_id=self.id_).debug("Page is closed successfully")
        except Exception as e:
            logger.bind(page_id=self.id_).error(f"Error during page cleanup: {e}")

    def update_last_used(self) -> None:
        self._last_used = datetime.now()

    @property
    def is_idle(self) -> bool:
        "Get page's status - idle if it hasn't been used in the last 3 minutes"
        if self._last_used < (datetime.now() - timedelta(seconds=conf.page_idle_timeout)):
            return True
        return False

    async def get_page_metrics(self) -> dict:
        dom_size = await self._page.evaluate("document.getElementsByTagName('*').length")
        navigation_timing = await self._page.evaluate("JSON.stringify(window.performance.timing)")
        resource_perf = await self._page.evaluate("JSON.stringify(window.performance.getEntries())")
        load_time = await self._page.evaluate(
            """() => performance.timing.loadEventEnd - performance.timing.navigationStart"""
        )
        viewport = self._page.viewport
        metrics = await self._page.metrics()

        return {
            "dom_size": dom_size,
            "navigation_timing": navigation_timing,
            "resource_perf": resource_perf,
            "load_time": load_time,
            "viewport": viewport,
            "metrics": metrics,
        }

    @pyd.validate_arguments
    @log_elapsed_time
    async def perform_page_action(self, action: PageActionType, **kwargs) -> Any:
        return_page_contents = kwargs.pop("returnPageContents", False)

        match action:
            case PageActionType.CLICK:
                call_method = perform_action_click

            case PageActionType.AUTHENTICATE:
                call_method = perform_action_authenticate

            case PageActionType.SET_USER_AGENT:
                call_method = perform_action_setUserAgent

            case PageActionType.SCREENSHOT:
                call_method = perform_action_screenshot

            case PageActionType.GOTO:
                call_method = perform_action_goto

            case PageActionType.GO_BACK:
                call_method = perform_action_goBack

            case PageActionType.GO_FORWARD:
                call_method = perform_action_goForward

            case PageActionType.EVALUATE:
                call_method = perform_action_evaluate

            case PageActionType.EXTRACT_PAGE_CONTENTS:
                call_method = perform_action_extractPageContents

            case PageActionType.EXPOSE_FUNCTION:
                call_method = perform_action_exposeFunction

            case PageActionType.REMOVE_FUNCTION:
                call_method = perform_action_removeFunction

            case PageActionType.SET_VIEWPORT:
                call_method = perform_action_setViewport

            case PageActionType.SET_GEOLOCATION:
                call_method = perform_action_setGeoLocation

            case PageActionType.CLEAR_GEOLOCATION:
                call_method = perform_action_clearGeolocation

            case PageActionType.ADD_SCRIPT_TAG:
                call_method = perform_action_addScriptTag

            case PageActionType.REMOVE_SCRIPT_TAG:
                call_method = perform_action_removeScriptTag

            case PageActionType.EVALUATE_HANDLE:
                call_method = perform_action_evaluateHandle

            case PageActionType.EVALUATE_ON_NEW_DOCUMENT:
                call_method = perform_action_evaluateOnNewDocument

            case PageActionType.SET_COOKIE:
                call_method = perform_action_setCookie

            case PageActionType.DELETE_COOKIE:
                call_method = perform_action_deleteCookie

            case PageActionType.EMULATE_MEDIA:
                call_method = perform_action_emulateMedia

            case PageActionType.START_JS_COVERAGE:
                call_method = perform_action_startJSCoverage

            case PageActionType.STOP_JS_COVERAGE:
                call_method = perform_action_stopJSCoverage

            case PageActionType.GET_PAGE_METRICS:
                call_method = self.get_page_metrics

            case PageActionType.GET_ACCESSIBILITY_TREE:
                call_method = perform_action_getAccessibilityTree

            case PageActionType.SET_CONTENT:
                call_method = perform_action_setContent

            case PageActionType.SET_EXTRA_HTTP_HEADERS:
                call_method = perform_action_setExtraHttpHeaders

            case _:
                raise NotImplementedError(f"Action '{action}' is not supported!")

        try:
            res = await call_method(self._page, **kwargs)
            if return_page_contents and action != PageActionType.EXTRACT_PAGE_CONTENTS:
                return await perform_action_extractPageContents(self._page)
            return res

        except Exception as e:
            logger.bind(session_id=str(self.id_), page_action=action).error(
                f"Unable to perform action - {e}"
            )
            raise UnableToPerformActionError(e)

        finally:
            self.update_last_used()
