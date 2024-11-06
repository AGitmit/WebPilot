from fastapi import APIRouter, status

from web_weaver.config import config as conf


router = APIRouter(prefix="")


@router.get("/", status_code=status.HTTP_200_OK, include_in_schema=False)
async def index():
    """Returns the service's basic information."""
    return dict(
        service="🕸️👻 WebWeaver",
        environment=conf.environment,
        version=conf.app_version,
    )
