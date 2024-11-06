from enum import Enum
from il_web_renderer.config import config as conf


class Templates(Enum):
    OWNERSHIPTREE = "OwnershipTree_template.html"
    SCOREGRAPH = "ScoreGraph_template.html"


class TempRoot(Enum):
    TEMPLATES = f"{conf.assets_base_url}/resources/templates/"
