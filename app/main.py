import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.auth import NotAuthenticatedException, get_current_member_optional
from app.database import create_db_and_tables, engine, get_session
from app.jinja import BASE_DIR, templates
from app.routers import public, private, guestbook
from app.seed import seed_members, seed_questions
from app.services.updates import seed_if_empty

SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    SECRET_KEY = "dev-fallback-change-me-in-production"


class CurrentMemberMiddleware(BaseHTTPMiddleware):
    """Attach the logged-in Member (or None) to request.state on every request."""

    async def dispatch(self, request: Request, call_next):
        request.state.current_member = get_current_member_optional(request)
        return await call_next(request)


app = FastAPI(title="Friends Group Website")

app.add_middleware(CurrentMemberMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="session",
    same_site="lax",
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(public.router)
app.include_router(private.router)
app.include_router(guestbook.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    session = next(get_session())
    try:
        seed_if_empty(session)
        seed_members(session)
        seed_questions(session)
    finally:
        session.close()


@app.exception_handler(NotAuthenticatedException)
async def not_authenticated_handler(request: Request, exc: NotAuthenticatedException):
    return RedirectResponse("/login", status_code=303)


@app.exception_handler(StarletteHTTPException)
async def not_found_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return HTMLResponse(str(exc.detail), status_code=exc.status_code)
