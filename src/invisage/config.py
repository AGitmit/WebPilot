import os

from pyppeteer import executablePath
from pydantic import BaseSettings, Field
from typing import Literal, Union


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
    chromium_path: str = Field(default_factory=executablePath)
    browser_headless: bool = Field(default=True)
    browser_auto_close: bool = Field(default=False)
    page_cache_ttl: float = Field(default=18_000)  # 5 hours
    page_cache_cap: int = Field(default=100)  # max page cache in memory

    # etc.
    temp_file_archive: str = f"{root_folder}/temp_archive"

    
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
