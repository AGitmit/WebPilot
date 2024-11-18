from fastapi import APIRouter, status, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from web_pilot.config import config as conf
from web_pilot.clients.pools_admin import PoolAdmin
from web_pilot.schemas.requests import PoolAdminCreateReq
from web_pilot.utils.limiter import rate_limiter


router = APIRouter(prefix=f"{conf.v1_url_prefix}/browser-pools", tags=["Browser-Pools"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    description="Create a new browser-pool",
    dependencies=[Depends(rate_limiter)],
)
async def create_browser_pool(config: PoolAdminCreateReq):
    pool_id = PoolAdmin.create_new_pool(config.dict(exclude_none=True))
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"pool_id": pool_id})


@router.get(
    "/list",
    status_code=status.HTTP_200_OK,
    description="List all browser-pools",
    dependencies=[Depends(rate_limiter)],
)
async def list_browsers():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"pools": PoolAdmin.list_pools()})


@router.get(
    "/{pool_id}",
    status_code=status.HTTP_200_OK,
    description="Get a browser-pool by its ID",
    dependencies=[Depends(rate_limiter)],
)
async def get_pool(pool_id: str):
    pool = PoolAdmin.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"pool": pool.__repr__()})


@router.delete(
    "/{pool_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a browser-pool by its ID",
    dependencies=[Depends(rate_limiter)],
)
async def delete_pool(pool_id: str, force: bool = Query(default=False)):
    PoolAdmin.delete_pool(pool_id, force)


@router.patch(
    "/{pool_id}/scale-up",
    status_code=status.HTTP_200_OK,
    description="Manually scale-up a browser-pool by its ID",
    dependencies=[Depends(rate_limiter)],
)
async def manual_scale_up(pool_id: str):
    pool = PoolAdmin.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found")

    pool.create_new_browser()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"pool": pool.__repr__()})


@router.patch(
    "/{pool_id}/scale-down",
    status_code=status.HTTP_200_OK,
    description="Manually scale-down a browser-pool by its ID (removes the least busy browser)",
    dependencies=[Depends(rate_limiter)],
)
async def manual_scale_down(pool_id: str):
    """
    Manually scale-down a browser-pool by its ID (removes the least busy browser)
    This operation is not reversible and will remove the least busy browser and all its sessions!
    """
    pool = PoolAdmin.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found")

    if not await pool.remove_browser_by_id(pool.get_least_busy_browser().id_, force=True):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Browser not found")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"pool": pool.__repr__()})
