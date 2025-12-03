#!/usr/bin/env bash
set -euo pipefail

# One-time / infrequent initialization helper for the app.

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

if [ ! -d "$VENV_DIR" ]; then
  echo "[init] Creating virtual environment at $VENV_DIR..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

echo "[init] Activating virtual environment..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "[init] Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
  echo "[init] .env not found. Copying from .env.example..."
  cp .env.example .env
  echo "[init] Please edit .env with your secrets/mail settings."
fi

export FLASK_APP=wsgi.py

echo "[init] Applying database migrations..."
flask db upgrade

echo "[init] Initialization complete."
