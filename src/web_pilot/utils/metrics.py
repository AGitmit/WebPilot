import time
import functools
import asyncio

from web_pilot.logger import logger


def log_execution_metrics(func):
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"{func.__name__} took {execution_time:.4f} seconds to complete.")
        return result

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"{func.__name__} took {execution_time:.4f} seconds to complete.")
        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# async def page_usage_metrics(self):
#     # gather and view usage of resources for current visited host
#     # Create a single CDP session
#     cdp_client = await self.page.target.createCDPSession()
#     metrics = await cdp_client.send("Performance.getMetrics")
#     storage = await cdp_client.send("Storage.getUsageAndQuota", {
#     "origin": self.page.url
#     })
