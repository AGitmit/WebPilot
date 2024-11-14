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
    log_file_location: str = "./logs/web_pilot.log"

    # pool admin config
    max_pools: int = 10
    idle_pool_deletion_interval: int = 30

    # browser pool config
    pool_max_size: int = 1
    max_cached_items: int = 100  # max pages cached in memory
    user_data_dir: str = f"./user_data"

    # Chromium
    chromium_path: str = Field(default_factory=executablePath)

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
