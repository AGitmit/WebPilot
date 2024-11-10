import pyppeteer
import pydantic as pyd

from web_pilot.logger import logger
from fake_useragent import UserAgent
from enum import Enum
from typing import Optional


class HeadlessUtil:
    _ua = UserAgent()

    class BrowserTypes(Enum):
        CHROME = "chrome"
        SAFARI = "safari"
        FIREFOX = "firefox"
        EDGE = "edge"

    class MobilePlatform(Enum):
        ANDROID = "android"
        IOS = "ios"

    @classmethod
    @pyd.validate_arguments
    def fake_user_agent(
        cls,
        type: Optional[BrowserTypes] = None,
        mobile: bool = False,
        platform: Optional[MobilePlatform] = None,
    ) -> str:
        """Returns a random string of a browser's user-agent; You can ask for a specific type of browser or completely random."""
        match type:
            case cls.BrowserTypes.CHROME:
                return cls._ua.googlechrome
            case cls.BrowserTypes.FIREFOX:
                return cls._ua.firefox
            case cls.BrowserTypes.EDGE:
                return cls._ua.edge
            case cls.BrowserTypes.SAFARI:
                return cls._ua.safari
            case _:
                return cls._ua.random

    @staticmethod
    def check_chromium():
        if not pyppeteer.chromium_downloader.check_chromium():
            logger.info("Downloading Chromium...")
            pyppeteer.chromium_downloader.download_chromium()
            logger.info("Chromium downloaded successfully")
