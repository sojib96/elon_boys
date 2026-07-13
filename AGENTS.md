# AGENTS.md — Friends Group Website

## Commands

```bash
# dev server (port 8001, not default 8000)
uvicorn app.main:app --reload --port 8001

# API tests — run directly against FastAPI (fast, no server needed)
pytest tests/test_public_routes.py -v

# run a single test
pytest tests/test_public_routes.py::TestPublicRoutes::test_homepage_title

# E2E tests — require dev server on port 8001 (or set TEST_URL env var)
# First-time setup: python -m playwright install chromium
pytest tests/e2e/ -v

# generate SECRET_KEY for .env
python -c "import secrets; print(secrets.token_urlsafe(32))"

# install deps
pip install -r requirements.txt
```

## Architecture

- **FastAPI** app in `app/main.py`. Routers: `public.py` (public pages), `private.py` (login, uploads, notes), `guestbook.py`.
- **All data is currently hardcoded** in the router files as lists of dicts. SQLModel tables are defined in `models.py` but not wired to routes yet.
- **`create_db_and_tables()`** in `database.py` exists but is never called — no automatic table creation on startup.
- **Jinja2 templates** in `app/templates/`. Tailwind CSS loaded via CDN (no build step, no package.json, no node_modules).
- **Session auth** is planned (routes exist) but not implemented — `/login`, `/uploads`, `/notes` pages render without protection.

## Key conventions

- **Port 8001** for local dev (not 8000). E2E tests default to `http://127.0.0.1:8001`.
- **Color palette**: terracotta `#b85c3e` / `#e85d3a` primary, amber `#f59e0b` accent, warm off-white `#faf7f2` background.
- **Database**: SQLite (`sqlite:///./data/friends.db`) locally, Supabase Postgres in production (via `DATABASE_URL` env var).
- **No form submissions or POST routes yet** — all routes are read-only GET.
- **DB driver**: SQLModel + psycopg2-binary for Postgres. Supabase Python client (`supabase`) available for Storage.
- **E2E test data expectations** mirror the hardcoded dicts — changing counts or content breaks tests.
- **Static uploads** go to `app/static/uploads/` (gitignored). `.gitkeep` preserves the directory.
- **`.env.example`** has all required env vars — copy to `.env` for local dev.

## Testing quirks

- `tests/test_auth.py` is empty — no auth tests exist yet.
- E2E tests use Playwright Python (`sync_api`), not JS Playwright.
- API tests use `TestClient` from `fastapi.testclient` — they import `app.main:app` directly.
- No pytest config file exists (no `pyproject.toml`, no `pytest.ini`).
- No linting or typechecking tools configured.

## Deployment

- Render Blueprint in `render.yaml` — builds with `pip install -r requirements.txt`, starts with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Push to `main` triggers auto-deploy.
- Supabase Storage `uploads` bucket for future file uploads.
