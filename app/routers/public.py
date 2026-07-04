from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.jinja import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/our-story", response_class=HTMLResponse)
async def our_story(request: Request):
    return templates.TemplateResponse("story.html", {"request": request})


@router.get("/squad", response_class=HTMLResponse)
async def squad(request: Request):
    return templates.TemplateResponse("squad.html", {"request": request})


@router.get("/timeline", response_class=HTMLResponse)
async def timeline(request: Request):
    return templates.TemplateResponse("timeline.html", {"request": request})


@router.get("/gallery", response_class=HTMLResponse)
async def gallery(request: Request):
    return templates.TemplateResponse("gallery.html", {"request": request})


@router.get("/updates", response_class=HTMLResponse)
async def updates(request: Request):
    return templates.TemplateResponse("updates.html", {"request": request})


@router.get("/events", response_class=HTMLResponse)
async def events(request: Request):
    return templates.TemplateResponse("events.html", {"request": request})


@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})
