import json
import uuid
import pydantic as pyd
import re

from typing import Optional
from web_pilot.schemas import sanitize_str
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

    # @pyd.validator()
    # def sanitize_str(cls, value: str):
    #     if re.search(sanitize_str, value):
    #         raise ValueError(
    #             f"Illegal characters found in '{value}' - allowed special characters are '-' or '_'"
    #         )
    #     return value

    class Config:
        extra = "allow"
