from enum import Enum


class PageActionType(Enum):
    CLICK = "click"
    AUTHENTICATE = "authenticate"
    SET_USER_AGENT = "setUserAgent"
    SCREENSHOT = "screenshot"
    GOTO = "goto"
    GO_BACK = "goBack"
    GO_FORWARD = "goForward"
    EVALUATE = "evaluate"
    SAVE_SNAPSHOT = "saveSnapshot"
    RESTORE_SNAPSHOT = "restoreSnapshot"
    SET_GEOLOCATION = "setGeoLocation"
    SET_VIEWPORT = "setViewport"
