import uuid
import asyncio

from fastapi import APIRouter, status, HTTPException
from web_weaver.config import config as conf
from web_weaver.clients.controller import BrowserController
from web_weaver.schemas.requests import FetchRequest, PageActionRequest
from web_weaver.schemas.responses import PageContentResponse
from web_weaver.logger import logger


router = APIRouter(prefix=f"{conf.v1_url_prefix}/browser", tags=["Headless Browser"])


@router.post("/fetch/url", response_model=PageContentResponse, status_code=status.HTTP_200_OK)
async def fetch_url(args: FetchRequest):
    with logger.contextualize(transaction_id=args.transaction_id):
        try:
            return await asyncio.wait_for(
                BrowserController.fetch_page_contents(**args.dict()),
                timeout=conf.default_timeout,
            )

        except asyncio.TimeoutError as e:
            msg = "Request has been timed-out!"
            logger.error(msg)
            raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=msg)

        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/sessions/page/open/{session_id}", status_code=status.HTTP_201_CREATED)
async def start_page_session(session_id: uuid.UUID):
    try:
        return await asyncio.wait_for(
            BrowserController.start_page_session(session_id), timeout=conf.default_timeout
        )

    except asyncio.TimeoutError as e:
        msg = "Request has been timed-out!"
        logger.error(msg)
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=msg)

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/sessions/page/close/{session_id}", status_code=status.HTTP_200_OK)
async def close_page_session(session_id: uuid.UUID):
    try:
        return await asyncio.wait_for(
            BrowserController.remove_cached_page(session_id), timeout=conf.default_timeout
        )

    except KeyError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=str(e))

    except asyncio.TimeoutError as e:
        msg = "Request has been timed-out!"
        logger.error(msg)
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=msg)

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/sessions/page/action/{session_id}",
    response_model=PageContentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def perform_action_on_page(session_id: uuid.UUID, args: PageActionRequest):
    async def action_on_page(session_id: uuid.UUID, args: PageActionRequest):
        page = await BrowserController.retrieve_cached_page(session_id)
        return await BrowserController.page_action(page, **args.dict())

    try:
        return await asyncio.wait_for(
            action_on_page(session_id, args), timeout=conf.default_timeout
        )

    except KeyError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=str(e))

    except asyncio.TimeoutError as e:
        msg = "Request has been timed-out!"
        logger.error(msg)
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=msg)

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))