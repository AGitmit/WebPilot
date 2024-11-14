from fastapi import APIRouter, status, HTTPException, Query
from fastapi.responses import JSONResponse
from web_pilot.config import config as conf
from web_pilot.clients.pools_admin import PoolAdmin
from web_pilot.schemas.requests import PoolAdminCreateReq


router = APIRouter(prefix=f"{conf.v1_url_prefix}/browser-pools", tags=["Browser-Pools"])


@router.post(
    "/create", status_code=status.HTTP_201_CREATED, description="Create a new browser-pool"
)
async def create_browser_pool(config: PoolAdminCreateReq):
    pool_id = PoolAdmin.create_new_pool(config.dict(exclude_none=True))
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"pool_id": pool_id})


@router.get("/list", status_code=status.HTTP_200_OK)
async def list_browsers():
    return JSONResponse(status_code=status.HTTP_200_OK, content=str(PoolAdmin.list_pools()))


@router.get("/{pool_id}", status_code=status.HTTP_200_OK)
async def get_pool(pool_id: str):
    pool = PoolAdmin.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"pool": str(pool)})


@router.delete("/{pool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pool(pool_id: str, force: bool = Query(default=False)):
    PoolAdmin.delete_pool(pool_id, force)
