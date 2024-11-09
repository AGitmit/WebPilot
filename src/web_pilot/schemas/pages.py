import pydantic as pyd


class PageContent(pyd.BaseModel):
    url: str
    title: str
    content: str


class Snapshot(pyd.BaseModel):
    url: str = pyd.Field(default="")
    cookies: dict = pyd.Field(default={})
    local_storage: dict = pyd.Field(default={})
    session_storage: dict = pyd.Field(default={})
    dom_state: dict = pyd.Field(default={})
    network_requests: list = pyd.Field(default=[])
    custom_scripts: list = pyd.Field(default=[])
    timestamp: str = pyd.Field(default="")
    user_agent: str = pyd.Field(default="")
    viewport_size: dict = pyd.Field(default={})
