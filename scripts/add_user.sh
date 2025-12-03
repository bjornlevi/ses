#!/usr/bin/env bash
set -euo pipefail

# Adds a user via CLI with optional admin flag.

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

if [ -d "$VENV_DIR" ]; then
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
fi

read -rp "Username: " USERNAME
read -rp "Email: " EMAIL
read -rsp "Password: " PASSWORD
echo
read -rsp "Confirm Password: " PASSWORD2
echo
if [ "$PASSWORD" != "$PASSWORD2" ]; then
  echo "Passwords do not match."
  exit 1
fi

read -rp "Make admin? [y/N]: " ADMIN
ADMIN=${ADMIN:-N}
ADMIN_FLAG=false
case "$ADMIN" in
  y|Y) ADMIN_FLAG=true ;;
esac

cat <<'PY' | APP_ADMIN_FLAG="$ADMIN_FLAG" APP_USERNAME="$USERNAME" APP_EMAIL="$EMAIL" APP_PASSWORD="$PASSWORD" "$PYTHON_BIN"
import os
from wsgi import app
from app import db
from app.models import User

username = os.environ["APP_USERNAME"]
email = os.environ["APP_EMAIL"].lower()
password = os.environ["APP_PASSWORD"]
is_admin = os.environ["APP_ADMIN_FLAG"].lower() == "true"

with app.app_context():
    existing = User.query.filter((User.email == email) | (User.username == username)).first()
    if existing:
        print("User with that email or username already exists.")
        raise SystemExit(1)
    user = User(email=email, username=username, confirmed=True, is_admin=is_admin)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"Created user {username} ({email}), admin={is_admin}")
PY
