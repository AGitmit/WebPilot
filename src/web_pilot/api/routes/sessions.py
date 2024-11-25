import asyncio

from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from web_pilot.clients.pools_admin import PoolAdmin
from web_pilot.config import config as conf
from web_pilot.schemas.requests import PageActionRequest, PageActionType
from web_pilot.schemas.responses import PageContentResponse
from web_pilot.logger import logger
from web_pilot.exc import PageSessionNotFoundError
from web_pilot.utils.limiter import rate_limiter


router = APIRouter(prefix=f"{conf.v1_url_prefix}/sessions", tags=["Page Sessions"])


@router.get(
    "/actions",
    status_code=status.HTTP_200_OK,
    description="List all supported page actions",
    dependencies=[Depends(rate_limiter)],
)
async def list_supported_page_actions():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"supported_actions": str([i.value for i in PageActionType.__members__.values()])},
    )


@router.get(
    "/new",
    status_code=status.HTTP_201_CREATED,
    description="Start a new, in-memory, remote, page session",
    dependencies=[Depends(rate_limiter)],
)
async def start_page_session(pool_id: str) -> str:
    pool = PoolAdmin.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found")

    browser = await pool.get_least_busy_browser(create_if_none=True)
    session_id = await browser.start_page_session(session_id_prefix=f"{pool.id_}_{browser.id_}")
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"session_id": session_id},
    )


@router.get("/{session_id}", status_code=status.HTTP_200_OK)
async def get_page_session_metrics(session_id: str):
    try:
        _, _, page_session = PoolAdmin.get_session_parent_chain(session_id, peek=True)
        response = await page_session.get_page_metrics()
        return JSONResponse(status_code=status.HTTP_200_OK, content=response)

    except PageSessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    except KeyError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=str(e))


@router.patch(
    "/close/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Close a remote page session",
    dependencies=[Depends(rate_limiter)],
)
async def close_page_session(session_id: str) -> None:
    try:
        _, browser, page_session = PoolAdmin.get_session_parent_chain(session_id)
        await browser.close_page_session(page_session.id_)

    except PageSessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    except KeyError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=str(e))


@router.post(
    "/action/{session_id}",
    response_model=PageContentResponse,
    status_code=status.HTTP_200_OK,
    description="Perform an action on a remote page session",
    dependencies=[Depends(rate_limiter)],
)
async def perform_action_on_page(session_id: str, args: PageActionRequest):
    with logger.contextualize(session_id=session_id, action=args.action.value):
        # helper function
        async def action_on_page(session_id: str, args: PageActionRequest):
            _, browser, page = PoolAdmin.get_session_parent_chain(session_id)
            response = await page.perform_page_action(**args.dict())
            browser.put_page_session(page.id_, page)
            return JSONResponse(status_code=status.HTTP_200_OK, content=response)

        try:
            return await asyncio.wait_for(
                action_on_page(session_id, args), timeout=conf.default_timeout
            )

        except KeyError as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=str(e))
