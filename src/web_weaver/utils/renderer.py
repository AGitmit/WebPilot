import pydantic as pyd

from web_weaver.utils.metrics import log_execution_metrics
from pyppeteer.page import Page


@pyd.validate_arguments
@log_execution_metrics
async def save_as_png(page: Page, width: int = 1200, height: int = 800) -> str | bytes:
    "Render page as PNG"
    await page.setViewport({"width": width, "height": height})
    png_image = await page.screenshot()
    return png_image


@pyd.validate_arguments
async def save_as_pdf(page: Page) -> bytes:
    "Render page as PDF"
    return await page.pdf()
