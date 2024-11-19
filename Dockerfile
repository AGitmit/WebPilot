FROM python:3.12-slim

# Set environment variables for Python and Poetry
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PATH="/app/.venv/bin:$PATH" \
    UVICORN_PATH=/app/.venv/bin/uvicorn \
    PYTHONPATH=/app/src

# Install essential build dependencies and Chromium for Pyppeteer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev libssl-dev make musl-dev chromium chromium-driver \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# Install Poetry and project dependencies (without dev dependencies)
RUN pip install --no-cache-dir --upgrade pip poetry \
    && poetry install --no-interaction --no-ansi --no-dev \
    && rm -rf $POETRY_CACHE_DIR

COPY . .

# Ensure permissions for the app user
RUN addgroup --system www && adduser --system --ingroup www appuser \
    && chgrp -R www ${VIRTUAL_ENV} /app && chmod -R u+rx ${VIRTUAL_ENV} /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.web_pilot.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
