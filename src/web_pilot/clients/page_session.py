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
        try:
            match action:
                case PageActionType.CLICK:
                    func_to_call = perform_action_click

                case PageActionType.AUTHENTICATE:
                    func_to_call = perform_action_authenticate

                case PageActionType.SET_USER_AGENT:
                    func_to_call = perform_action_setUserAgent

                case PageActionType.SCREENSHOT:
                    func_to_call = perform_action_screenshot

                case PageActionType.GOTO:
                    func_to_call = perform_action_goto

                case PageActionType.GO_BACK:
                    func_to_call = perform_action_goBack

                case PageActionType.GO_FORWARD:
                    func_to_call = perform_action_goForward

                case PageActionType.SAVE_SNAPSHOT:
                    func_to_call = perform_action_saveSnapshot

                case PageActionType.RESTORE_SNAPSHOT:
                    func_to_call = perform_action_restoreSnapshot

                case PageActionType.EVALUATE:
                    func_to_call = perform_action_evaluate

            return await func_to_call(self._page, **kwargs)
            # return await perform_action_extractPageContents(self._page)

        except Exception as e:
            logger.bind(
                browser_id=self.parent, session_id=str(self.session_id), page_action=action
            ).error(f"Unable to perform action - {e}")
            raise UnableToPerformActionError(e)
