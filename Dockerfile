# Use an official Python image as a base
FROM python:3.12-slim

# Set the working directory to /app
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=./src

# Copy the application code
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir .
# Install Chromium dependencies
RUN apt-get update && apt-get install -y \
    libx11-6 \
    libx11-xcb-dev \
    libxcb-dri3-0 \
    libxcb-present0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxshmfence1 \
    libxtst6

# Download and install Chromium
RUN apt-get update && apt-get install -y chromium

# Set environment variables
ENV ENVIRONMENT=localhost
ENV HOST_ADDRESS=0.0.0.0
ENV HOST_PORT=8000
ENV DEFAULT_TIMEOUT=60
ENV WORKERS_COUNT=1
ENV RATE_LIMIT=100
ENV RATE_PERIOD=60
ENV LOG_LEVEL=INFO
ENV EXPORT_LOGS=False
ENV LOG_FILE_LOCATION=./logs
ENV CHROMIUM_PATH=/usr/bin/chromium
ENV USER_DATA_DIR=./user_data
ENV MAX_POOLS=10
ENV IDLE_POOL_DELETION_INTERVAL=30
ENV BROWSER_POOL_MAX_SIZE=1
ENV BROWSER_MAX_CACHED_ITEMS=100
ENV PAGE_IDLE_TIMOUT=180
ENV CACHE_PROVIDER=in_memory
ENV CACHE_TTL=3600

# Expose the port
EXPOSE 8000

# Run the command to start the development server
CMD ["python", "-m", "uvicorn", "web_pilot.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]