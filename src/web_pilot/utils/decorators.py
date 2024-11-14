import asyncio
import functools
import time

from web_pilot.logger import logger


def repeat_every(interval: int):
    def wrapper(func):
        async def async_wrapper(*args, **kwargs):
            try:
                while True:
                    await func(*args, **kwargs)
                    await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in exectuion of repeating function: {e}")

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                while True:
                    func(*args, **kwargs)
                    time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in exectuion of repeating function: {e}")

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return wrapper
