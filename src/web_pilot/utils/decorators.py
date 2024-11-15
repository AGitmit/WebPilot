import asyncio
import functools
import time

from web_pilot.logger import logger
from web_pilot.exc import PoolIsInactiveError


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


def run_if_browser_accepts_new_jobs(func) -> callable:
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._accept_new_jobs:
            raise PoolIsInactiveError("Pool is inactive")

        # Check at call time whether to use async or sync execution
        if asyncio.iscoroutinefunction(func):
            # Use an inner async function when called in an async context
            async def async_wrapper():
                return await func(self, *args, **kwargs)

            return async_wrapper()  # Call immediately, returns a coroutine
        # Otherwise, just call synchronously
        return func(self, *args, **kwargs)

    return wrapper
