import asyncio

from fastapi import FastAPI, HTTPException, status
from web_pilot.api.routes import router as IndexRouter
from web_pilot.api.routes.browser_pool import router as BrowserPoolRouter
from web_pilot.api.routes.sessions import router as SessionsRouter
from web_pilot.config import config as conf
from web_pilot.utils.headless import HeadlessUtil
from web_pilot.clients.pools_admin import PoolAdmin
from web_pilot.utils.decorators import repeat_every
from web_pilot.exc import PoolIsInactiveError, PoolAlreadyExistsError, NoAvailableBrowserError


app = FastAPI(
    title="🌐🕹️ WebPilot API",
    version=conf.app_version,
    description="Controlling the web - Redefined!",
    openapi_url=f"{conf.v1_url_prefix}/openapi.json",
    docs_url=f"{conf.v1_url_prefix}/docs",
    redoc_url=f"{conf.v1_url_prefix}/redoc",
)

for router in [
    IndexRouter,
    BrowserPoolRouter,
    SessionsRouter,
]:
    app.include_router(router)


# Error handlers
@app.exception_handler(Exception)
async def http_exception_handler(request, exc):
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@app.exception_handler(PoolIsInactiveError)
async def pool_inactive_handler(request, exc):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@app.exception_handler(PoolAlreadyExistsError)
async def pool_already_exists_handler(request, exc):
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@app.exception_handler(NoAvailableBrowserError)
async def no_available_browser_handler(request, exc):
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))


@app.exception_handler(asyncio.TimeoutError)
async def timeout_handler(request, exc):
    raise HTTPException(
        status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request has been timed-out!"
    )


# Background tasks
@app.on_event("startup")
async def check_chromium():
    HeadlessUtil.check_chromium()


@repeat_every(interval=conf.idle_pool_deletion_interval)
async def delete_unused_pools():
    PoolAdmin.remove_deletion_candidates()


@app.on_event("startup")
async def register_background_tasks():
    asyncio.create_task(delete_unused_pools())
