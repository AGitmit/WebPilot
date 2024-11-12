import asyncio
import uuid

from fastapi import APIRouter, status, HTTPException, Query
from fastapi.responses import JSONResponse
from web_pilot.config import config as conf
from web_pilot.clients.pools_admin import PoolAdmin
from web_pilot.schemas.requests import PoolAdminCreateReq
from web_pilot.logger import logger
from web_pilot.exc import BrowserPoolCapacityReachedError, PoolAlreadyExistsError


router = APIRouter(prefix=f"{conf.v1_url_prefix}/browser-pools", tags=["Browser-Pools"])


@router.post(
    "/create", status_code=status.HTTP_201_CREATED, description="Create a new browser-pool"
)
async def create_browser_pool(config: PoolAdminCreateReq):
    try:
        pool_id = PoolAdmin.create_new_pool(config.dict(exclude_none=True))
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"pool_id": pool_id})

    except PoolAlreadyExistsError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

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


@router.get("/list", status_code=status.HTTP_200_OK)
async def list_browsers():
    return JSONResponse(status_code=status.HTTP_200_OK, content=str(PoolAdmin.list_pools()))


@router.get("/{pool_id}", status_code=status.HTTP_200_OK)
async def get_pool(pool_id: str):
    try:
        pool = PoolAdmin.get_pool(pool_id)
        if not pool:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found")

        return JSONResponse(status_code=status.HTTP_200_OK, content={"pool": str(pool)})

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{pool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pool(pool_id: str, force: bool = Query(default=False)):
    try:
        PoolAdmin.delete_pool(pool_id, force)

    except asyncio.TimeoutError as e:
        msg = "Request has been timed-out!"
        logger.error(msg)
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=msg)

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
