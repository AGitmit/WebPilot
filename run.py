import uvicorn

from web_pilot.config import config as conf


if __name__ == "__main__":
    uvicorn.run(
        "web_pilot.api.app:app",
        host=conf.host_address,
        port=conf.host_port,
        access_log=True,
        reload=conf.reload_app,
        workers=conf.workers_count,
        loop="uvloop",
    )
