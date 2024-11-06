import pydantic as pyd


class PageContentResponse(pyd.BaseModel):
    url: str
    title: str | None
    content: str | None
    cookies: list | None
