from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.main import templates

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("private/login.html", {"request": request})


@router.get("/uploads", response_class=HTMLResponse)
async def uploads(request: Request):
    return templates.TemplateResponse("private/uploads.html", {"request": request})


@router.get("/notes", response_class=HTMLResponse)
async def notes(request: Request):
    return templates.TemplateResponse("private/notes.html", {"request": request})
