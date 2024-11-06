import sys

from loguru import logger
from web_weaver.config import config as conf


def init_logger(**context):
    "Set up a new logger"
    logger.remove()
    logger.add(
        sys.stdout,
        level=conf.log_level,
        enqueue=True,
        colorize=True,
        format="{time} | {level} | {extra} | {message}",
        backtrace=True,
        diagnose=True,
    )
    logger.configure(extra=context or {"source": "Internal"})
    return logger


logger = init_logger()
