FROM python:3.11-alpine as builder
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev 
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir --upgrade pip poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \ 
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache


RUN poetry install --no-interaction --no-dev --no-ansi && rm -rf $POETRY_CACHE_DIR
FROM python:3.11-alpine3.18 as production
RUN apk add --no-cache --update chromium chromium-chromedriver && rm -rf /var/cache/apk/*
RUN apk upgrade
ENV PYTHONPATH=/app/src
ENV UVICORN_PATH=/usr/local/bin/uvicorn
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
RUN addgroup -S www && adduser -S appuser -G www
COPY --from=builder  ${VIRTUAL_ENV} ${VIRTUAL_ENV}
WORKDIR /app
COPY . .
RUN mkdir /app/src/il_web_renderer/temp_archive
RUN chgrp -R www ${VIRTUAL_ENV} /app && chmod -R  u+rx ${VIRTUAL_ENV} /app
RUN chmod -R  777 /app/src/il_web_renderer/temp_archive
USER appuser
EXPOSE 8000
CMD ["uvicorn", "il_web_renderer.api.app:app", "--host", "0.0.0.0", "--port", "8000"]

