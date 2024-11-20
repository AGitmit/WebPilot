import pyppeteer

from web_pilot.logger import logger


class HeadlessUtil:
    @staticmethod
    def check_chromium():
        if not pyppeteer.chromium_downloader.check_chromium():
            logger.info("Downloading Chromium...")
            pyppeteer.chromium_downloader.download_chromium()
            logger.info("Chromium downloaded successfully")
        logger.debug("Chromium is up to date")
