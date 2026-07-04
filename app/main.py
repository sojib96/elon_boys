from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.jinja import BASE_DIR
from app.routers import public, private, guestbook

app = FastAPI(title="Friends Group Website")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(public.router)
app.include_router(private.router)
app.include_router(guestbook.router)
