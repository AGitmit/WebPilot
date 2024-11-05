from fastapi import FastAPI

# relative imports
from il_web_renderer.api.routes.render import router as RenderRouter
from il_web_renderer.api.routes import router as IndexRouter
from il_web_renderer.api.routes.browser import router as BrowserRouter
from il_web_renderer.config import config as conf


app = FastAPI(
    title="il-Web-Renderer",
    version=conf.app_version,
    description="A Headless-browser HTTP API application powered by Pyppeteer",
)

for router in [
    IndexRouter,
    RenderRouter,
    BrowserRouter,
]:
    app.include_router(router)
