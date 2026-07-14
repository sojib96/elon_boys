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
    {"id": 1, "name": "Alex Chen", "nickname": "Ace", "email": "alex.chen@elonboys.com", "photo_url": None, "image1": "/static/img/members/cover.jpg", "image2": "/static/img/members/alex-cover.jpg", "bio": "CS grad who somehow survived 8AM algorithms. Now building things at Google.", "fun_fact": "Once coded a chatbot that only spoke in memes.", "current_status": "Software Engineer at Google", "quote": "I wrote more bug reports than features that first year. The group chat was my only working dependency.", "tag": "THE BUILDER"},
    {"id": 2, "name": "Maya Rodriguez", "nickname": "Mae", "email": "maya.rodriguez@elonboys.com", "photo_url": None, "image1": "/static/img/members/profile.jpg", "image2": "/static/img/members/maya-cover.jpg", "bio": "Biology nerd who spent more time in the lab than her dorm room.", "fun_fact": "Can name every bone in the human body — and still can't parallel park.", "current_status": "Medical Resident at NYU Langone", "quote": "I spent more time in the lab than my dorm room. They brought me food so I wouldn't starve.", "tag": "THE HEALER"},
    {"id": 3, "name": "James Okafor", "nickname": "Jay", "email": "james.okafor@elonboys.com", "photo_url": None, "image1": "/static/img/members/img-1099.jpeg", "image2": "/static/img/members/james-cover.jpg", "bio": "Business school escapee who turned a dorm-room idea into a real company.", "fun_fact": "Negotiated a pizza discount that lasted all four years.", "current_status": "Founder & CEO of Kola", "quote": "I turned a pizza discount into a pitch deck. Nobody was surprised.", "tag": "THE FOUNDER"},
    {"id": 4, "name": "Priya Sharma", "nickname": "Pri", "email": "priya.sharma@elonboys.com", "photo_url": None, "image1": "/static/img/members/safi-cover.jpg", "image2": "/static/img/members/priya-cover.jpg", "bio": "Aerospace engineering with a minor in late-night chai debates.", "fun_fact": "Her thesis was 4 pages over the limit — she fought for it and won.", "current_status": "Propulsion Engineer at NASA JPL", "quote": "My thesis was four pages over the limit. I fought for every single one.", "tag": "THE ROCKET"},
    {"id": 5, "name": "Leo Kim", "nickname": "LK", "email": "leo.kim@elonboys.com", "photo_url": None, "image1": "/static/img/members/safi-thumb.jpg", "image2": "/static/img/members/leo-cover.jpg", "bio": "Design major who made our group look way cooler than we actually were.", "fun_fact": "Designed the group's unofficial logo during a 3AM coffee run.", "current_status": "UX Designer at Figma", "quote": "I designed our group logo at 3AM over cold coffee. It's still my best work.", "tag": "THE AESTHETE"},
    {"id": 6, "name": "Sara Johansson", "nickname": "Saz", "email": "sara.johansson@elonboys.com", "photo_url": None, "image1": "/static/img/members/sara-thumb.jpg", "image2": None, "bio": "English lit major who wrote everyone's love letters (whether we asked or not).", "fun_fact": "Her poetry slam went viral on campus radio.", "current_status": "Freelance Writer & Editor", "quote": "I wrote everyone's love letters. Some of them even worked.", "tag": "THE WORDSMITH"},
    {"id": 7, "name": "David Park", "nickname": "DP", "email": "david.park@elonboys.com", "photo_url": None, "image1": "/static/img/members/david-thumb.jpg", "image2": None, "bio": "History buff who somehow made every conversation about the Roman Empire.", "fun_fact": "Can recite the Gettysburg Address from memory — backwards.", "current_status": "High School History Teacher", "quote": "I once connected everything to the Roman Empire. Everything.", "tag": "THE HISTORIAN"},
    {"id": 8, "name": "Aisha Mohammed", "nickname": "Aish", "email": "aisha.mohammed@elonboys.com", "photo_url": None, "image1": "/static/img/members/aisha-thumb.jpg", "image2": None, "bio": "Pre-med with a secret talent for stand-up comedy during study breaks.", "fun_fact": "Never pulled an all-nighter — witchcraft, according to the rest of us.", "current_status": "Pediatric Resident at Children's Hospital", "quote": "I never pulled a single all-nighter. They still haven't forgiven me.", "tag": "THE ENIGMA"},
    {"id": 9, "name": "Tomás Silva", "nickname": "T", "email": "tomas.silva@elonboys.com", "photo_url": None, "image1": "/static/img/members/tomas-thumb.jpg", "image2": None, "bio": "Music major who recorded our group's unofficial anthem in a broom closet.", "fun_fact": "His playlist 'Study Beats 2020' has 2 million streams on Spotify.", "current_status": "Music Producer & Audio Engineer", "quote": "I recorded our anthem in a broom closet. Two million people listened.", "tag": "THE PRODUCER"},
    {"id": 10, "name": "Yuki Tanaka", "nickname": "Yuk", "email": "yuki.tanaka@elonboys.com", "photo_url": None, "image1": "/static/img/members/yuki-thumb.jpg", "image2": None, "bio": "Architecture student who built a cardboard castle for our final-year party.", "fun_fact": "Speaks four languages, still can't say 'no' to free food.", "current_status": "Junior Architect at SOM Tokyo", "quote": "I built a cardboard castle for our final party. It collapsed. We didn't care.", "tag": "THE ARCHITECT"},
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
