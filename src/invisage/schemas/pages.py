import pydantic as pyd


class PageContent(pyd.BaseModel):
    url: str
    title: str
    content: str


class Snapshot(pyd.BaseModel):
    url: str
    cookies: dict
    local_storage: dict
    session_storage: dict
