from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from app.database import get_session
from app.jinja import templates
from app.models import GalleryItem, GuestbookEntry, Member, UpdatePost
from app.services import gallery as gallery_svc
from app.services import updates as updates_svc

router = APIRouter()

TIMELINE_EVENTS = [
    {"id": 1, "year": 1, "title": "First Day of University", "description": "Ten strangers walked into the same lecture hall. None of us knew we'd just met our best friends.", "photo_urls": None},
    {"id": 2, "year": 1, "title": "Dorm Floor Dinner", "description": "Our first group dinner — instant noodles, bad pizza, and the beginning of a tradition that lasted four years.", "photo_urls": None},
    {"id": 3, "year": 1, "title": "Freshman Freshers' Week", "description": "Survived freshers' week together. We bonded over terrible icebreakers and a shared confusion about campus maps.", "photo_urls": None},
    {"id": 4, "year": 1, "title": "First Group Photo", "description": "Someone pulled out a camera and we all squeezed into frame. That photo still sits on everyone's phone.", "photo_urls": None},
    {"id": 5, "year": 2, "title": "Spring Break Road Trip", "description": "Rented a beat-up van and drove 12 hours to the coast. The van broke down. We didn't care.", "photo_urls": None},
    {"id": 6, "year": 2, "title": "Late-Night Study Sessions", "description": "Countless nights in the library basement — fuelled by coffee, despair, and someone's smuggled snacks.", "photo_urls": None},
    {"id": 7, "year": 2, "title": "University Festival", "description": "We ran a stall at the uni festival. It lost money. We gained memories.", "photo_urls": None},
    {"id": 8, "year": 2, "title": "Secret Santa", "description": "Our first Secret Santa. David got everyone the same mug. He said it was 'a theme'.", "photo_urls": None},
    {"id": 9, "year": 3, "title": "House Share Begins", "description": "Moved into our first shared house. The boiler broke on day one. We called it home anyway.", "photo_urls": None},
    {"id": 10, "year": 3, "title": "Birthday Surprise", "description": "Pulled off a surprise birthday for one of us — complete with a cake that was 70% icing. She cried.", "photo_urls": None},
    {"id": 11, "year": 3, "title": "Summer Internships", "description": "We scattered across the country for internships. The group chat kept us going.", "photo_urls": None},
    {"id": 12, "year": 3, "title": "Halloween Party", "description": "Ten costumes, one tiny living room, and a playlist that went until 4AM. The neighbours loved us.", "photo_urls": None},
    {"id": 13, "year": 4, "title": "Final Year Project Madness", "description": "All-nighters, printer breakdowns, and last-minute panics. We somehow all graduated.", "photo_urls": None},
    {"id": 14, "year": 4, "title": "Graduation Day", "description": "Caps in the air, tears in our eyes, and one last group photo that still makes us smile.", "photo_urls": None},
    {"id": 15, "year": 4, "title": "Farewell Dinner", "description": "Our last dinner together as students. We promised to stay close — and we kept that promise.", "photo_urls": None},
    {"id": 16, "year": 4, "title": "The Afterparty", "description": "We stayed up until sunrise, went through every photo on every phone, and cried more than we'd like to admit.", "photo_urls": None},
]



EVENTS_LIST = [
    {"id": 1, "title": "Summer Reunion 2026", "date": "2026-08-15", "description": "Our first official reunion at the old campus. Dinner, drinks, and a walk down memory lane. Partners welcome!", "is_upcoming": True},
    {"id": 2, "title": "Beach Day", "date": "2026-09-10", "description": "A day at the beach — just like the old road trip. Bring snacks and sunscreen. Bonus points if you bring that inflatable flamingo.", "is_upcoming": True},
    {"id": 3, "title": "Board Game Night", "date": "2026-07-25", "description": "Monthly virtual board game night. David always wins at Catan. This time will be different. (It won't.)", "is_upcoming": True},
    {"id": 4, "title": "New Year's Eve 2025", "date": "2025-12-31", "description": "Ring in the new year together over Zoom, just like we used to. Fireworks, bad champagne, and great company.", "is_upcoming": False},
    {"id": 5, "title": "Graduation Anniversary Dinner", "date": "2025-07-04", "description": "Celebrating four years since we tossed our caps in the air. Same diner, same booth, same friends.", "is_upcoming": False},
    {"id": 6, "title": "Winter Potluck", "date": "2024-12-20", "description": "Everyone brought something they'd learned to cook. The fire alarm went off twice. Best night of the year.", "is_upcoming": False},
]

MEMBERS = [
    {"id": 1, "name": "Alex Chen", "nickname": "Ace", "photo_url": None, "image1": "/static/img/members/cover.jpg", "image2": "/static/img/members/alex-cover.jpg", "bio": "CS grad who somehow survived 8AM algorithms. Now building things at Google.", "fun_fact": "Once coded a chatbot that only spoke in memes.", "current_status": "Software Engineer at Google", "quote": "I wrote more bug reports than features that first year. The group chat was my only working dependency.", "tag": "THE BUILDER"},
    {"id": 2, "name": "Maya Rodriguez", "nickname": "Mae", "photo_url": None, "image1": "/static/img/members/profile.jpg", "image2": "/static/img/members/maya-cover.jpg", "bio": "Biology nerd who spent more time in the lab than her dorm room.", "fun_fact": "Can name every bone in the human body — and still can't parallel park.", "current_status": "Medical Resident at NYU Langone", "quote": "I spent more time in the lab than my dorm room. They brought me food so I wouldn't starve.", "tag": "THE HEALER"},
    {"id": 3, "name": "James Okafor", "nickname": "Jay", "photo_url": None, "image1": "/static/img/members/img-1099.jpeg", "image2": "/static/img/members/james-cover.jpg", "bio": "Business school escapee who turned a dorm-room idea into a real company.", "fun_fact": "Negotiated a pizza discount that lasted all four years.", "current_status": "Founder & CEO of Kola", "quote": "I turned a pizza discount into a pitch deck. Nobody was surprised.", "tag": "THE FOUNDER"},
    {"id": 4, "name": "Priya Sharma", "nickname": "Pri", "photo_url": None, "image1": "/static/img/members/safi-cover.jpg", "image2": "/static/img/members/priya-cover.jpg", "bio": "Aerospace engineering with a minor in late-night chai debates.", "fun_fact": "Her thesis was 4 pages over the limit — she fought for it and won.", "current_status": "Propulsion Engineer at NASA JPL", "quote": "My thesis was four pages over the limit. I fought for every single one.", "tag": "THE ROCKET"},
    {"id": 5, "name": "Leo Kim", "nickname": "LK", "photo_url": None, "image1": "/static/img/members/safi-thumb.jpg", "image2": "/static/img/members/leo-cover.jpg", "bio": "Design major who made our group look way cooler than we actually were.", "fun_fact": "Designed the group's unofficial logo during a 3AM coffee run.", "current_status": "UX Designer at Figma", "quote": "I designed our group logo at 3AM over cold coffee. It's still my best work.", "tag": "THE AESTHETE"},
    {"id": 6, "name": "Sara Johansson", "nickname": "Saz", "photo_url": None, "image1": "/static/img/members/sara-thumb.jpg", "image2": None, "bio": "English lit major who wrote everyone's love letters (whether we asked or not).", "fun_fact": "Her poetry slam went viral on campus radio.", "current_status": "Freelance Writer & Editor", "quote": "I wrote everyone's love letters. Some of them even worked.", "tag": "THE WORDSMITH"},
    {"id": 7, "name": "David Park", "nickname": "DP", "photo_url": None, "image1": "/static/img/members/david-thumb.jpg", "image2": None, "bio": "History buff who somehow made every conversation about the Roman Empire.", "fun_fact": "Can recite the Gettysburg Address from memory — backwards.", "current_status": "High School History Teacher", "quote": "I once connected everything to the Roman Empire. Everything.", "tag": "THE HISTORIAN"},
    {"id": 8, "name": "Aisha Mohammed", "nickname": "Aish", "photo_url": None, "image1": "/static/img/members/aisha-thumb.jpg", "image2": None, "bio": "Pre-med with a secret talent for stand-up comedy during study breaks.", "fun_fact": "Never pulled an all-nighter — witchcraft, according to the rest of us.", "current_status": "Pediatric Resident at Children's Hospital", "quote": "I never pulled a single all-nighter. They still haven't forgiven me.", "tag": "THE ENIGMA"},
    {"id": 9, "name": "Tomás Silva", "nickname": "T", "photo_url": None, "image1": "/static/img/members/tomas-thumb.jpg", "image2": None, "bio": "Music major who recorded our group's unofficial anthem in a broom closet.", "fun_fact": "His playlist 'Study Beats 2020' has 2 million streams on Spotify.", "current_status": "Music Producer & Audio Engineer", "quote": "I recorded our anthem in a broom closet. Two million people listened.", "tag": "THE PRODUCER"},
    {"id": 10, "name": "Yuki Tanaka", "nickname": "Yuk", "photo_url": None, "image1": "/static/img/members/yuki-thumb.jpg", "image2": None, "bio": "Architecture student who built a cardboard castle for our final-year party.", "fun_fact": "Speaks four languages, still can't say 'no' to free food.", "current_status": "Junior Architect at SOM Tokyo", "quote": "I built a cardboard castle for our final party. It collapsed. We didn't care.", "tag": "THE ARCHITECT"},
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
        .limit(3)
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
        .limit(1)
    ).first()

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


@router.get("/timeline", response_class=HTMLResponse)
async def timeline(request: Request):
    years = {}
    for event in TIMELINE_EVENTS:
        years.setdefault(event["year"], []).append(event)
    return templates.TemplateResponse("timeline.html", {"request": request, "years": years})


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
