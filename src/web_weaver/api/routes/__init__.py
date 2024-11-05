from fastapi import APIRouter, status

# relative imports
from il_web_renderer.config import config as conf


router = APIRouter(prefix="")


@router.get("/", status_code=status.HTTP_200_OK, include_in_schema=False)
async def index():
    """Returns the service's basic information."""
    return dict(
        service="Web-Renderer",
        environment=conf.environment,
        version=conf.app_version,
    )
