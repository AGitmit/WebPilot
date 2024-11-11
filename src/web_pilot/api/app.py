from fastapi import FastAPI

from web_pilot.api.routes import router as IndexRouter
from web_pilot.api.routes.browser import router as BrowserRouter
from web_pilot.config import config as conf
from web_pilot.utils.headless import HeadlessUtil


app = FastAPI(
    title="👨‍✈️ WebPilot API",
    version=conf.app_version,
    description="Controlling the web - redefined!",
    openapi_url=f"{conf.v1_url_prefix}/openapi.json",
    docs_url=f"{conf.v1_url_prefix}/docs",
    redoc_url=f"{conf.v1_url_prefix}/redoc",
)

for router in [
    IndexRouter,
    BrowserRouter,
]:
    app.include_router(router)


@app.on_event("startup")
async def check_chromium():
    HeadlessUtil.check_chromium()