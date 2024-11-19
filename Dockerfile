FROM python:3.12-slim

# Install essential build dependencies and Chromium for Pyppeteer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev libssl-dev make musl-dev chromium chromium-driver \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# Set environment variables for Python and Poetry
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app/src

# Install Poetry and project dependencies (without dev dependencies)
RUN pip install --no-cache-dir --upgrade pip poetry \
    && poetry install --only main --no-ansi \
    && rm -rf $POETRY_CACHE_DIR \

COPY . .

# Ensure permissions for the app user
RUN addgroup --system www && adduser --system --ingroup www appuser \
    && chgrp -R www /app/.venv /app && chmod -R u+rx /app/.venv /app

USER appuser

EXPOSE 8000

CMD python3 run.py
