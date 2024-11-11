from enum import Enum


class PageActionType(Enum):
    CLICK = "click"
    AUTHENTICATE = "authenticate"
    SET_USER_AGENT = "set_ua"
    SCREENSHOT = "screenshot"
    GOTO = "go_to"
    GO_BACK = "go_back"
    GO_FORWARD = "go_forward"
    EVALUATE = "evaluate"
    SAVE_SNAPSHOT = "save_snapshot"
    RESTORE_SNAPSHOT = "restore_snapshot"
    SET_GEOLOCATION = "set_geolocation"
    SET_VIEWPORT = "set_viewport"
