# Debate Hub Flask App

A Flask app for debating opinions with structured arguments and reasoning. Supports user registration with email confirmation, Markdown content, and admin controls.

## Quickstart (local)
1. Create venv & install deps:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configure env:
   ```bash
   cp .env.example .env
   # edit .env with SECRET_KEY, mail settings, optional APP_URL_PREFIX
   export FLASK_APP=wsgi.py
   ```
3. Init DB:
   ```bash
   flask db upgrade
   ```
4. Run:
   ```bash
   flask run
   ```

## Deployment helpers
- `scripts/init_app.sh`: set up venv, install deps, copy `.env` if missing, run migrations.
- `scripts/reload.sh`: `git pull --rebase`, restart `ses.service`, reload nginx.
- `scripts/add_user.sh`: CLI prompt to add a user (optionally admin, auto-confirmed).

Make scripts executable: `chmod +x scripts/*.sh`.

## Features
- Users: register/login, email confirmation (Flask-Mail), optional app prefix (`APP_URL_PREFIX`).
- Opinions: concise Markdown opinions require an initial argument + reasoning.
- Arguments: for/against per opinion, Markdown, view reasons.
- Reasoning: Markdown per argument.
- Admin: promote/demote admins, block/unblock users via `/admin/users`; blocked users are signed out and denied login.
- Markdown rendering with sanitization (markdown2 + bleach).

## Routes (prefix-aware)
If `APP_URL_PREFIX` is set (e.g., `/debate`), all routes and static assets include it:
- `/` list opinions
- `/opinions/new` create opinion + first argument/reasoning
- `/opinions/<id>` opinion detail with for/against sections
- `/opinions/<id>/arguments/new?stance=for|against` add argument (stance prefilled)
- `/arguments/<id>` argument detail + reasons
- `/arguments/<id>/reasoning/new` add reasoning
- `/register`, `/login`, `/logout`
- `/confirm/<token>` email confirmation
- `/admin/users` admin panel (admins only)

## Notes
- SQLite by default; override with `DATABASE_URL`.
- Set `SERVER_NAME` in `.env` to help generate absolute links in emails if needed.
- Gunicorn/nginx service names assumed as `ses.service` and `nginx`; adjust scripts if your environment differs.
