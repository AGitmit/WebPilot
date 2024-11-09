import asyncio
import uuid

from typing import Optional
from fastapi import APIRouter, status, HTTPException, Query
from fastapi.responses import JSONResponse
from web_pilot.config import config as conf
from web_pilot.clients.manager import BrowserManager
from web_pilot.logger import logger
from web_pilot.exc import BrowserPoolCapacityReachedError


router = APIRouter(prefix=f"{conf.v1_url_prefix}/browser", tags=["Headless Browser"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_browser(config: Optional[dict] = None):
    try:
        browser_id = await asyncio.wait_for(
            BrowserManager.create_new_browser(config), timeout=conf.default_timeout
        )
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"browser_id": browser_id})

    except BrowserPoolCapacityReachedError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except asyncio.TimeoutError as e:
        msg = "Request has been timed-out!"
        logger.error(msg)
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=msg)

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/remove/{browser_id}", status_code=status.HTTP_204_NO_CONTENT)
async def create_browser(browser_id: uuid.UUID, force: bool = Query(default=False)):
    try:
        await BrowserManager.remove_browser_by_id(browser_id, force)

    except asyncio.TimeoutError as e:
        msg = "Request has been timed-out!"
        logger.error(msg)
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=msg)

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/list", status_code=status.HTTP_200_OK)
async def list_browsers():
    return JSONResponse(
        status_code=status.HTTP_200_OK, content=[str(b) for b in BrowserManager.browsers]
    )
