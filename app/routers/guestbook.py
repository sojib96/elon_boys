from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.jinja import templates

router = APIRouter()

GUESTBOOK_ENTRIES = [
    {"id": 1, "name": "Sarah M.", "message": "This website is such a beautiful idea! The memories you guys have are priceless. ❤️", "posted_at": "2026-06-20"},
    {"id": 2, "name": "Prof. Anderson", "message": "So wonderful to see this group still thriving after all these years. You were always my favourite class!", "posted_at": "2026-06-18"},
    {"id": 3, "name": "Mike R.", "message": "I was your RA in Year 1. You guys were a handful, but you turned out amazing. So proud!", "posted_at": "2026-06-15"},
    {"id": 4, "name": "Emily T.", "message": "Love the timeline feature — brought back so many memories of our uni days together.", "posted_at": "2026-06-10"},
    {"id": 5, "name": "David's Mom", "message": "You all grew up so well. Thank you for being such good friends to my son.", "posted_at": "2026-06-05"},
]


@router.get("/guestbook", response_class=HTMLResponse)
async def guestbook_page(request: Request):
    return templates.TemplateResponse("guestbook.html", {"request": request, "entries": GUESTBOOK_ENTRIES})
