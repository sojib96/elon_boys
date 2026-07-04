from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.main import templates

router = APIRouter()


@router.get("/guestbook", response_class=HTMLResponse)
async def guestbook_page(request: Request):
    return templates.TemplateResponse("guestbook.html", {"request": request})
