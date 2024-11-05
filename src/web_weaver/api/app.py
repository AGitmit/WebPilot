from fastapi import FastAPI

from web_weaver.api.routes import router as IndexRouter
from web_weaver.api.routes.browser import router as BrowserRouter
from web_weaver.config import config as conf


app = FastAPI(
    title="🕸️👻 WebWeaver API",
    version=conf.app_version,
    description="Automated web - Reimagined",
    openapi_url=f"{conf.v1_url_prefix}/openapi.json",
    docs_url=f"{conf.v1_url_prefix}/docs",
    redoc_url=f"{conf.v1_url_prefix}/redoc",
)

for router in [
    IndexRouter,
    BrowserRouter,
]:
    app.include_router(router)
