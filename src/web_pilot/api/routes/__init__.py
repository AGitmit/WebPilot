from fastapi import APIRouter, status

from web_pilot.config import config as conf
from web_pilot.clients.pools_admin import PoolAdmin


router = APIRouter(prefix="")


@router.get("/", status_code=status.HTTP_200_OK, include_in_schema=False)
@router.get("/{conf.v1_url_prefix}", status_code=status.HTTP_200_OK, include_in_schema=False)
async def index():
    """Returns the service's basic information."""
    return dict(
        service="🌐🕹️ WebPilot",
        environment=conf.environment,
        version=conf.app_version,
        activity={
            "pools": PoolAdmin.list_pools(),
        },
    )
