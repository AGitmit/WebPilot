import pydantic as pyd

from typing import Optional
from web_pilot.schemas.constants.page_action_type import PageActionType


class PoolAdminCreateReq(pyd.BaseModel):
    headless: Optional[bool]
    incognito: Optional[bool]
    gpu: Optional[bool]
    privacy: Optional[bool]
    ignore_http_errors: Optional[bool]
    spa_mode: Optional[bool]
    proxy_server: Optional[str]
    platform: Optional[str]
    browser: Optional[str]

    class Config:
        extra = "forbid"


class PageActionRequest(pyd.BaseModel):
    action: PageActionType

    class Config:
        extra = "allow"
