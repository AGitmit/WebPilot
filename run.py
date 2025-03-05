import uvicorn

from web_pilot.config import config as conf


if __name__ == "__main__":
    uvicorn.run(
        "web_pilot.api.app:app",
        host=conf.host_address,
        port=conf.host_port,
        access_log=True,
        workers=conf.workers_count,
        limit_concurrency=conf.limit_concurrency,
        limit_max_requests=conf.limit_max_requests,
        loop="uvloop",
    )
