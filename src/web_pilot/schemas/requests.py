import json
import uuid
import pydantic as pyd
import re

from typing import Optional
from web_pilot.schemas import sanitize_str
from web_pilot.schemas.constants.page_action_type import PageActionType


class PageActionRequest(pyd.BaseModel):
    action: PageActionType
    selector: str | None = pyd.Field(default=None)
    options: dict | None = pyd.Field(default=None)
    credentials: dict | None = pyd.Field(default=None)
    user_agent: str | None = pyd.Field(default=None)
    url: str | None = pyd.Field(default=None)

    @pyd.validator("url")
    def sanitize_str(cls, value: str):
        if re.search(sanitize_str, value):
            raise ValueError(
                f"Illegal characters found in '{value}' - allowed special characters are '-' or '_'"
            )
        return value

    class Config:
        extra = "allow"
