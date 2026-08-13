#!/bin/bash

# PythonAnywhere setup helper script
# Run this from the project root after cloning the repository.

set -e

echo "Checking Python version..."
PYTHON_CMD=""
for ver in python3.11 python3.10 python3.9 python3; do
  if command -v "$ver" >/dev/null 2>&1; then
    PYTHON_CMD="$ver"
    break
  fi
done

if [ -z "$PYTHON_CMD" ]; then
  echo "ERROR: No Python 3 executable found. Please install Python 3 on PythonAnywhere." >&2
  exit 1
fi

echo "Using $PYTHON_CMD"

if [ ! -d "$HOME/virtualenvs" ]; then
  mkdir -p "$HOME/virtualenvs"
fi

VENV_PATH="$HOME/virtualenvs/fuocomplaint"

if [ ! -d "$VENV_PATH" ]; then
  echo "Creating virtualenv at $VENV_PATH"
  $PYTHON_CMD -m venv "$VENV_PATH"
else
  echo "Virtualenv already exists at $VENV_PATH"
fi

echo "Activating virtualenv"
source "$VENV_PATH/bin/activate"

echo "Installing dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete."
echo "Next steps:"
echo " 1) In PythonAnywhere Web tab, set the source directory to: $PWD"
echo " 2) Set the virtualenv path to: $VENV_PATH"
echo " 3) Set the WSGI configuration to use wsgi.py in the repo root"
echo " 4) Reload the web app"
