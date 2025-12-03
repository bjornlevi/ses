#!/usr/bin/env bash
set -euo pipefail

# Reloads the app by pulling latest code and restarting services.

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

echo "[reload] Updating code from git..."
git pull --rebase --stat

echo "[reload] Restarting gunicorn service (ses.service)..."
sudo systemctl restart ses.service

echo "[reload] Reloading nginx..."
sudo systemctl reload nginx || sudo systemctl restart nginx

echo "[reload] Done."
