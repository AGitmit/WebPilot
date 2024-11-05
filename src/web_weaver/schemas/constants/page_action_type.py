from enum import Enum


class PageActionType(Enum):
    CLICK = "click"
    AUTHENTICATE = "authenticate"
    SET_USER_AGENT = "set_ua"
    SCREENSHOT = "screenshot"
    GOTO = "go_to"
    GO_BACK = "go_back"
    GO_FORWARD = "go_forward"
