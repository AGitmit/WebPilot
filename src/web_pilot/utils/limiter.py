from fastapi import Request
from time import time
from web_pilot.config import config as conf
from web_pilot.exc import RateLimitsExceededError


RATE_LIMIT = conf.rate_limit
RATE_PERIOD = conf.rate_period  # Time period in seconds

request_count = {}


def rate_limiter(request: Request):
    client_ip = request.client.host
    current_time = time()

    if client_ip not in request_count:
        request_count[client_ip] = []

    # Filter out old requests
    request_count[client_ip] = [
        timestamp
        for timestamp in request_count[client_ip]
        if current_time - timestamp < RATE_PERIOD
    ]

    if len(request_count[client_ip]) >= RATE_LIMIT:
        raise RateLimitsExceededError("Rate limits exceeded!")

    request_count[client_ip].append(current_time)
