import asyncio
import os

from fastapi import APIRouter, status, HTTPException

from il_web_renderer.schemas.requests import ScoreGraphRequest, OwnershipTreeRequest
from il_web_renderer.schemas.responses import Base64OfImageResponse
from il_web_renderer.services.renderer import RendererService
from il_web_renderer.config import config as conf
from il_web_renderer.logger import logger


router = APIRouter(prefix=f"{conf.v1_url_prefix}/render", tags=["Render"])


@router.post(
    "/parts/ScoreGraph", response_model=Base64OfImageResponse, status_code=status.HTTP_201_CREATED
)
async def render_ScoreGraph(sg_req: ScoreGraphRequest):
    with logger.contextualize(transaction_id=sg_req.transaction_id):
        try:
            return await asyncio.wait_for(
                RendererService.render_report_part(**sg_req.dict()), timeout=conf.default_timeout
            )

        except asyncio.TimeoutError as e:
            msg = "Request has been timed-out!"
            logger.error(msg)
            raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=msg)

        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        finally:
            os.system(f"rm -rf {conf.temp_file_archive}/{str(sg_req.transaction_id)}")


@router.post(
    "/parts/OwnershipTree",
    response_model=Base64OfImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def render_ownership_tree(ot_req: OwnershipTreeRequest):
    with logger.contextualize(transaction_id=ot_req.transaction_id):
        try:
            return await asyncio.wait_for(
                RendererService.render_report_part(**ot_req.dict()), timeout=conf.default_timeout
            )

        except asyncio.TimeoutError as e:
            msg = "Request has been timed-out!"
            logger.error(msg)
            raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=msg)

        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        finally:
            os.system(f"rm -rf {conf.temp_file_archive}/{str(ot_req.transaction_id)}")
