from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from app.database import get_session
from app.jinja import templates
from app.models import GalleryItem, GuestbookEntry, Member, UpdatePost
from app.services import gallery as gallery_svc
from app.services import updates as updates_svc

router = APIRouter()


EVENTS_LIST = [
    {"id": 1, "title": "Summer Reunion 2026", "date": "2026-08-15", "description": "Our first official reunion at the old campus. Dinner, drinks, and a walk down memory lane. Partners welcome!", "is_upcoming": True},
    {"id": 2, "title": "Beach Day", "date": "2026-09-10", "description": "A day at the beach — just like the old road trip. Bring snacks and sunscreen. Bonus points if you bring that inflatable flamingo.", "is_upcoming": True},
    {"id": 3, "title": "Board Game Night", "date": "2026-07-25", "description": "Monthly virtual board game night. David always wins at Catan. This time will be different. (It won't.)", "is_upcoming": True},
    {"id": 4, "title": "New Year's Eve 2025", "date": "2025-12-31", "description": "Ring in the new year together over Zoom, just like we used to. Fireworks, bad champagne, and great company.", "is_upcoming": False},
    {"id": 5, "title": "Graduation Anniversary Dinner", "date": "2025-07-04", "description": "Celebrating four years since we tossed our caps in the air. Same diner, same booth, same friends.", "is_upcoming": False},
    {"id": 6, "title": "Winter Potluck", "date": "2024-12-20", "description": "Everyone brought something they'd learned to cook. The fire alarm went off twice. Best night of the year.", "is_upcoming": False},
]

MEMBERS = [
    {"id": 1, "name": "Md Sojib", "username": "sojib@elonboys", "nickname": "", "email": "20101030@uap-bd.edu", "photo_url": None, "image1": None, "image2": None, "bio": "", "fun_fact": "", "current_status": "", "quote": "", "tag": ""},
    {"id": 2, "name": "Md. Nazmul Islam Nayem", "username": "nayem@elonboys", "nickname": "", "email": "20101013@uap-bd.edu", "photo_url": None, "image1": None, "image2": None, "bio": "", "fun_fact": "", "current_status": "", "quote": "", "tag": ""},
    {"id": 3, "name": "Md. Mehedi Hasan", "username": "mehedi@elonboys", "nickname": "", "email": "20101007@uap-bd.edu", "photo_url": None, "image1": None, "image2": None, "bio": "", "fun_fact": "", "current_status": "", "quote": "", "tag": ""},
    {"id": 4, "name": "Apurba Datta", "username": "apurba@elonboys", "nickname": "", "email": "20101040@uap-bd.edu", "photo_url": None, "image1": None, "image2": None, "bio": "", "fun_fact": "", "current_status": "", "quote": "", "tag": ""},
    {"id": 5, "name": "Farhan Jarif Nibir", "username": "nibir@elonboys", "nickname": "", "email": "20101053@uap-bd.edu", "photo_url": None, "image1": None, "image2": None, "bio": "", "fun_fact": "", "current_status": "", "quote": "", "tag": ""},
    {"id": 6, "name": "Safi Ullah Chowdhury", "username": "safi@elonboys", "nickname": "", "email": "20101010@uap-bd.edu", "photo_url": None, "image1": None, "image2": None, "bio": "", "fun_fact": "", "current_status": "", "quote": "", "tag": ""},
    {"id": 7, "name": "Niaz Mahmud", "username": "niaz@elonboys", "nickname": "", "email": "20101019@uap-bd.edu", "photo_url": None, "image1": None, "image2": None, "bio": "", "fun_fact": "", "current_status": "", "quote": "", "tag": ""},
    {"id": 8, "name": "Al Zubayer Saad", "username": "saad@elonboys", "nickname": "", "email": "20101027@uap-bd.edu", "photo_url": None, "image1": None, "image2": None, "bio": "", "fun_fact": "", "current_status": "", "quote": "", "tag": ""},
    {"id": 9, "name": "MAHIR TAJWAR BHUIYAN", "username": "mahir@elonboys", "nickname": "", "email": "20101034@uap-bd.edu", "photo_url": None, "image1": None, "image2": None, "bio": "", "fun_fact": "", "current_status": "", "quote": "", "tag": ""},
    {"id": 10, "name": "Md. Rufiad Rahi Arnob", "username": "arnob@elonboys", "nickname": "", "email": "20101006@uap-bd.edu", "photo_url": None, "image1": None, "image2": None, "bio": "", "fun_fact": "", "current_status": "", "quote": "", "tag": ""},
    {"id": 11, "name": "Mahfuj Mahtab Mohot", "username": "mohot@elonboys", "nickname": "", "email": "19201003@uap-bd.edu", "photo_url": None, "image1": None, "image2": None, "bio": "", "fun_fact": "", "current_status": "", "quote": "", "tag": ""},
]


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, session: Session = Depends(get_session)):
    slider_images = session.exec(
        select(GalleryItem)
        .where(GalleryItem.is_deleted == False)
        .order_by(GalleryItem.uploaded_at.desc())
        .limit(10)
    ).all()

    latest_updates = session.exec(
        select(UpdatePost)
        .where(UpdatePost.is_deleted == False)
        .order_by(UpdatePost.posted_at.desc())
        .limit(4)
    ).all()

    gallery_strip = session.exec(
        select(GalleryItem)
        .where(GalleryItem.is_deleted == False)
        .order_by(GalleryItem.uploaded_at.desc())
        .limit(6)
    ).all()

    members = session.exec(select(Member).order_by(Member.id)).all()

    latest_guestbook = session.exec(
        select(GuestbookEntry)
        .order_by(GuestbookEntry.posted_at.desc())
        .limit(3)
    ).all()

    return templates.TemplateResponse("home.html", {
        "request": request,
        "slider_images": slider_images,
        "latest_updates": latest_updates,
        "gallery_strip": gallery_strip,
        "members": members,
        "latest_guestbook": latest_guestbook,
    })


@router.get("/our-story", response_class=HTMLResponse)
async def our_story(request: Request):
    return templates.TemplateResponse("story.html", {"request": request})


@router.get("/squad", response_class=HTMLResponse)
async def squad(request: Request, session: Session = Depends(get_session)):
    members = session.exec(select(Member).order_by(Member.id)).all()
    return templates.TemplateResponse("squad.html", {"request": request, "members": members})


@router.get("/squad/{member_id:int}", response_class=HTMLResponse)
async def member_detail(request: Request, member_id: int, session: Session = Depends(get_session)):
    member = session.get(Member, member_id)
    return templates.TemplateResponse("member_detail.html", {"request": request, "member": member})


@router.get("/gallery", response_class=HTMLResponse)
async def gallery(
    request: Request,
    session: Session = Depends(get_session),
):
    items, _total = gallery_svc.list_gallery(session)
    all_categories = session.exec(select(GalleryItem.category).distinct()).all()
    categories = sorted(set(all_categories))
    member = getattr(request.state, "current_member", None)
    return templates.TemplateResponse("gallery.html", {
        "request": request,
        "gallery_items": items,
        "categories": categories,
        "member": member,
    })


@router.get("/updates", response_class=HTMLResponse)
async def updates(request: Request, session: Session = Depends(get_session)):
    posts = updates_svc.list_updates(session)
    return templates.TemplateResponse("updates.html", {"request": request, "updates": posts})


@router.get("/updates/{update_id:int}", response_class=HTMLResponse)
async def update_detail(request: Request, update_id: int, session: Session = Depends(get_session)):
    post = updates_svc.get_update(session, update_id)
    if not post:
        raise HTTPException(status_code=404)
    related = updates_svc.get_related(session, exclude_id=update_id)
    member = getattr(request.state, "current_member", None)
    hero_intro, content_blocks = updates_svc.build_content_blocks(post)

    return templates.TemplateResponse("update_detail.html", {
        "request": request, "post": post, "related": related, "member": member,
        "hero_intro": hero_intro, "content_blocks": content_blocks,
    })


@router.get("/events", response_class=HTMLResponse)
async def events(request: Request):
    return templates.TemplateResponse("events.html", {"request": request, "events_list": EVENTS_LIST})


@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})
