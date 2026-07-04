from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.jinja import templates

router = APIRouter()

PRIVATE_UPLOADS = [
    {"id": 1, "file_url": None, "title": "Graduation video (raw)", "uploaded_by": "Alex", "uploaded_at": "2026-06-20"},
    {"id": 2, "file_url": None, "title": "Road trip blooper reel", "uploaded_by": "Maya", "uploaded_at": "2026-06-18"},
    {"id": 3, "file_url": None, "title": "House party photos", "uploaded_by": "James", "uploaded_at": "2026-06-15"},
    {"id": 4, "file_url": None, "title": "Secret Santa outtakes", "uploaded_by": "Priya", "uploaded_at": "2026-06-10"},
]

INTERNAL_NOTES = [
    {"id": 1, "author": "Alex", "message": "Who's bringing the grill to the reunion?", "posted_at": "2026-06-22"},
    {"id": 2, "author": "Maya", "message": "I can bring chairs and a cooler. Also, does anyone have the old playlist?", "posted_at": "2026-06-22"},
    {"id": 3, "author": "James", "message": "I've got the playlist! It's called 'Uni Vibes' and it's still on my Spotify.", "posted_at": "2026-06-21"},
    {"id": 4, "author": "Priya", "message": "Can someone pick up Sara from the airport on the 14th?", "posted_at": "2026-06-20"},
]


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("private/login.html", {"request": request})


@router.get("/uploads", response_class=HTMLResponse)
async def uploads(request: Request):
    return templates.TemplateResponse("private/uploads.html", {"request": request, "uploads": PRIVATE_UPLOADS})


@router.get("/notes", response_class=HTMLResponse)
async def notes(request: Request):
    return templates.TemplateResponse("private/notes.html", {"request": request, "notes_list": INTERNAL_NOTES})
