import pydantic as pyd
import pyppeteer

from typing import Any
from web_pilot.schemas.constants.page_action_type import PageActionType
from web_pilot.logger import logger
from web_pilot.utils.metrics import log_execution_metrics
from web_pilot.exc import UnableToPerformActionError
from web_pilot.utils.sessions import (
    perform_action_click,
    perform_action_authenticate,
    perform_action_setUserAgent,
    perform_action_screenshot,
    perform_action_goto,
    perform_action_goBack,
    perform_action_goForward,
    perform_action_saveSnapshot,
    perform_action_restoreSnapshot,
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
)


class PageSession:
    _page: pyppeteer.page.Page
    session_id: str
    parent: str

    def __init__(self, page_obj: pyppeteer.page.Page, page_id: int, **kwargs) -> None:
        self._page = page_obj
        self.id_ = page_id

    @property
    def id(self) -> int:
        return self.id_

    @id.setter
    def id(self, page_id: int) -> None:
        self.id_ = page_id

    def __repr__(self) -> str:
        return f"Page(id={self.session_id}, parent={self.id_.split('_')[0:2]})"

    @property
    def page(self) -> pyppeteer.page.Page:
        return self._page

    @page.setter
    def page(self, page_obj: pyppeteer.page.Page) -> None:
        self._page = page_obj

    @pyd.validate_arguments
    @log_execution_metrics
    async def perform_page_action(self, action: PageActionType, **kwargs) -> Any:
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

            case PageActionType.SAVE_SNAPSHOT:
                call_method = perform_action_saveSnapshot

            case PageActionType.RESTORE_SNAPSHOT:
                call_method = perform_action_restoreSnapshot

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

            case PageActionType.REMOVE_COOKIE:
                call_method = perform_action_deleteCookie

            case _:
                raise NotImplementedError(f"Action '{action}' is not supported!")

        try:
            return await call_method(self._page, **kwargs)

        except Exception as e:
            logger.bind(
                browser_id=self.parent, session_id=str(self.session_id), page_action=action
            ).error(f"Unable to perform action - {e}")
            raise UnableToPerformActionError(e)
