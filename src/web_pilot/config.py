import os

from pyppeteer import executablePath
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Literal, Union
from web_pilot.schemas.constants.cache import CacheProvider


class BaseConfig(BaseSettings):
    # app config
    environment: Literal["production", "staging", "localhost"]
    app_version: str = "0.1.0"
    v1_url_prefix: str = "/api/v1"
    root_folder: str = os.path.dirname(__file__)
    rate_limit: int = 100  # Number of requests over rate_period
    rate_period: int = 60  # Time period in seconds
    limit_concurrency: int = 100
    limit_max_requests: int = 5000
    access_log: bool = True if limit_concurrency < 200 else False
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
    pools_scaling_check_interval: int = 60

    # browser pool config
    browser_pool_max_size: int = 1
    browser_max_cached_items: int = 100  # max pages cached in memory
    user_data_dir: str = "./user_data"

    # Page Session config
    page_idle_timeout: int = 180  # 3 minutes

    # Chromium
    chromium_path: str = Field(default_factory=executablePath)

    # caching
    cache_ttl: float = 300  # 5 minutes
    cache_provider: CacheProvider = CacheProvider.IN_MEMORY
    cache_cleanup_interval: int = 60  # 1 minute

    class Config:
        case_sensitive = False
        env_file = ".env"
        extra = "allow"


class ProdConfig(BaseConfig):
    environment: Literal["production"]
    log_level: Literal["INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    workers_count: int = 7
    debug: bool = False


class DevConfig(BaseConfig):
    environment: Literal["staging", "localhost"]
    log_level: Literal["DEBUG", "INFO"] = "DEBUG"
    workers_count: int = 1
    debug: bool = True


def get_configuration() -> Union[DevConfig, ProdConfig]:
    environment_name = BaseConfig().environment
    config = {"staging": DevConfig, "production": ProdConfig}
    configuration_class = config.get(environment_name, DevConfig)
    return configuration_class()


config = get_configuration()
