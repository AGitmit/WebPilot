#!/bin/sh

set -e  # Exit on failure

PYTHON_VERSION="3.12"
VENV_DIR=".venv"

echo "Checking for Python $PYTHON_VERSION installation..."
# Try to use system Python first
if command -v python$PYTHON_VERSION >/dev/null 2>&1; then
    PYTHON_BIN="python$PYTHON_VERSION"
elif command -v pyenv >/dev/null 2>&1; then
    # Check if pyenv has the required version
    if pyenv versions | grep -q "$PYTHON_VERSION"; then
        echo "Found Python $PYTHON_VERSION via pyenv."
        pyenv local $PYTHON_VERSION
    else
        echo "Python $PYTHON_VERSION not found in pyenv. Installing..."
        pyenv install $PYTHON_VERSION
        pyenv local $PYTHON_VERSION
    fi
    PYTHON_BIN="$(pyenv which python3)"
else
    echo "❌ Python $PYTHON_VERSION is not installed, and pyenv is missing."
    echo "Please install Python $PYTHON_VERSION manually or install pyenv:"
    echo "🔹 MacOS (Homebrew): brew install pyenv"
    echo "🔹 Ubuntu: sudo apt install -y python3.12"
    echo "🔹 Arch Linux: sudo pacman -S python3.12"
    echo "Exiting..."
    exit 1
fi

echo "Using Python binary: $PYTHON_BIN"
$PYTHON_BIN --version
# USE_PYTHON=$($PYTHON_BIN --version | awk '{print $2}')
# echo $USE_PYTHON

echo "Checking for virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Setting up..."
    python3.12 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install .
    echo "Virtual environment setup complete."
else
    echo "Virtual environment found. Ensuring it's using Python $PYTHON_VERSION..."
    source "$VENV_DIR/bin/activate"
    CURRENT_VENV_PYTHON=$(poetry run python --version | awk '{print $2}')
    if [[ "$CURRENT_VENV_PYTHON" != "$PYTHON_VERSION"* ]]; then
        echo "Incorrect Python version in virtual environment. Recreating..."
        source "$VENV_DIR/bin/activate"
    fi
fi

echo "Checking for .env file..."
if [ ! -f ".env" ]; then
    if [ -f ".env.default" ]; then
        cp .env.default .env
        echo ".env file created from .env.default - modify as needed."
    else
        touch .env
        echo ".env file created - please configure it."
    fi
fi

echo "Starting project..."
exec poetry run python -m main
