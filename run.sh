#!/bin/sh

set -e  # Exit on failure

echo "Checking for virtual environment..."

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Setting up..."
    python3 -m venv .venv
    . .venv/bin/activate
    pip install poetry
    poetry install
    echo "Virtual environment setup complete."
else
    echo "Virtual environment found. Skipping setup..."
    . .venv/bin/activate
fi

if [ ! -d ".env" ]; then
    echo "Setting up .env file..."
    touch .env
    cp .env.default .env
    echo ".env file ready - modify as needed."
fi

echo "Starting project..."
exec python3 -m run
