import pydantic as pyd

from fake_useragent import UserAgent
from enum import Enum
from typing import Optional


class BrowserTypes(Enum):
    CHROME = "chrome"
    SAFARI = "safari"
    FIREFOX = "firefox"
    EDGE = "edge"


class Platform(Enum):
    WIN32 = "win32"
    WIN64 = "win64"
    MACINTEL = "MacIntel"
    MACPPC = "MacPPC"
    LINUX32 = "Linux i686"
    LINUX64 = "Linux x86_64"
    LINUXARM = "Linux armv7l"
    LINUXARM64 = "Linux aarch64"
    ANDROID = "Android"
    IPHONE = "iPhone"
    IPAD = "iPad"


_ua = UserAgent()


@pyd.validate_arguments
def fake_user_agent(
    type: Optional[BrowserTypes] = None,
) -> str:
    """Returns a random string of a browser's user-agent; You can ask for a specific type of browser or completely random."""
    match type:
        case BrowserTypes.CHROME:
            return _ua.googlechrome
        case BrowserTypes.FIREFOX:
            return _ua.firefox
        case BrowserTypes.EDGE:
            return _ua.edge
        case BrowserTypes.SAFARI:
            return _ua.safari
        case _:
            return _ua.random
