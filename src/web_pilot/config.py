import os

from pyppeteer import executablePath
from pydantic import BaseSettings, Field
from typing import Literal, Union
from web_pilot.schemas.constants.cache import CacheProvider


class BaseConfig(BaseSettings):
    # app config
    environment: Literal["production", "staging", "localhost"]
    app_version: str = "0.1.0"
    v1_url_prefix: str = "/api/v1"
    root_folder: str = os.path.dirname(__file__)

    # server config
    host_address: str = "0.0.0.0"
    host_port: int = 8000
    default_timeout: int = 60

    # logging config
    export_logs: bool = False
    log_file_location: str = root_folder

    # browser config
    auto_scale: bool = (
        True  # This ignores which browser is used and evenly splits the load between all browsers
    )
    balance_load: bool = True
    max_browsers_cap: int = 1
    max_cached_items: int = 100  # max pages cached in memory
    browser_config_file: str = f"{root_folder}/default_browser_config.json"
    # Chromium
    chromium_path: str = Field(default_factory=executablePath)
    # etc.
    temp_file_archive: str = f"{root_folder}/temp_archive"
    # caching
    cache_ttl: float = 3600  # 1 hour
    cache_provider: CacheProvider = CacheProvider.IN_MEMORY

    class Config:
        case_sensitive = False
        env_file = ".env"
        extra = "allow"


class ProdConfig(BaseConfig):
    environment: Literal["production"]
    log_level: Literal["INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    workers_count: int = 7
    debug: bool = False
    reload_app: bool = False


class DevConfig(BaseConfig):
    environment: Literal["staging", "localhost"]
    log_level: Literal["DEBUG", "INFO"] = "DEBUG"
    workers_count: int = 1
    debug: bool = True
    reload_app: bool = True


def get_configuration() -> Union[DevConfig, ProdConfig]:
    environment_name = BaseConfig().environment
    config = {"staging": DevConfig, "production": ProdConfig}
    configuration_class = config.get(environment_name, DevConfig)
    return configuration_class()


config = get_configuration()
