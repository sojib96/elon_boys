from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.jinja import templates

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

GALLERY_ITEMS = [
    {"id": 1, "category": "Events", "title": "Farewell Party 2024", "uploaded_by": "Alex"},
    {"id": 2, "category": "Trips", "title": "Beach Road Trip", "uploaded_by": "Maya"},
    {"id": 3, "category": "Campus Life", "title": "Library Shenanigans", "uploaded_by": "James"},
    {"id": 4, "category": "Events", "title": "Birthday Surprise", "uploaded_by": "Priya"},
    {"id": 5, "category": "Trips", "title": "Mountain Hike", "uploaded_by": "Leo"},
    {"id": 6, "category": "Random", "title": "Late Night Pizza", "uploaded_by": "Sara"},
    {"id": 7, "category": "Campus Life", "title": "Exam Week Madness", "uploaded_by": "David"},
    {"id": 8, "category": "Events", "title": "Festival Stall", "uploaded_by": "Aisha"},
    {"id": 9, "category": "Trips", "title": "Weekend Camping", "uploaded_by": "Tomás"},
    {"id": 10, "category": "Random", "title": "Group Selfie Collection", "uploaded_by": "Yuki"},
    {"id": 11, "category": "Events", "title": "Graduation Ceremony", "uploaded_by": "Alex"},
    {"id": 12, "category": "Campus Life", "title": "Dorm Room Chronicles", "uploaded_by": "Maya"},
    {"id": 13, "category": "Events", "title": "Halloween Costume Party", "uploaded_by": "Tomás"},
    {"id": 14, "category": "Trips", "title": "Sunrise Hike", "uploaded_by": "Leo"},
    {"id": 15, "category": "Random", "title": "Kitchen Dance Party", "uploaded_by": "Sara"},
    {"id": 16, "category": "Campus Life", "title": "Snow Day Fights", "uploaded_by": "Aisha"},
    {"id": 17, "category": "Events", "title": "Secret Santa 2022", "uploaded_by": "David"},
    {"id": 18, "category": "Trips", "title": "Lake House Weekend", "uploaded_by": "Yuki"},
]

UPDATES = [
    {"id": 1, "title": "Five Years Since Graduation", "content": "Can you believe it's been five years? We're planning a reunion this summer. Details coming soon — save the date for August 15th!", "author": "Alex Chen", "posted_at": "2026-06-15"},
    {"id": 2, "title": "Welcome to the Website!", "content": "We finally have a permanent home for all our memories. This is where we'll keep our photos, stories, and updates. Welcome back, everyone.", "author": "The Group", "posted_at": "2026-06-01"},
    {"id": 3, "title": "New Addition to the Squad", "content": "Big news — Maya and her partner just welcomed a baby girl! Little Sofia already has the whole group wrapped around her finger. Mazel tov!", "author": "Priya Sharma", "posted_at": "2026-05-20"},
    {"id": 4, "title": "Tomás Dropped a New Track", "content": "Our very own music producer just released a new single. It's called 'Nostalgia' and yes, there's a sample of our graduation night in there. Go stream it!", "author": "Leo Kim", "posted_at": "2026-04-10"},
    {"id": 5, "title": "Remembering the House", "content": "James found a video from our old house share. It's 3 minutes of chaos, burnt toast, and someone falling off a chair. It's perfect.", "author": "Sara Johansson", "posted_at": "2026-03-05"},
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
    {"id": 1, "name": "Alex Chen", "nickname": "Ace", "photo_url": None, "bio": "CS grad who somehow survived 8AM algorithms. Now building things at Google.", "fun_fact": "Once coded a chatbot that only spoke in memes.", "current_status": "Software Engineer at Google"},
    {"id": 2, "name": "Maya Rodriguez", "nickname": "Mae", "photo_url": None, "bio": "Biology nerd who spent more time in the lab than her dorm room.", "fun_fact": "Can name every bone in the human body — and still can't parallel park.", "current_status": "Medical Resident at NYU Langone"},
    {"id": 3, "name": "James Okafor", "nickname": "Jay", "photo_url": None, "bio": "Business school escapee who turned a dorm-room idea into a real company.", "fun_fact": "Negotiated a pizza discount that lasted all four years.", "current_status": "Founder & CEO of Kola"},
    {"id": 4, "name": "Priya Sharma", "nickname": "Pri", "photo_url": None, "bio": "Aerospace engineering with a minor in late-night chai debates.", "fun_fact": "Her thesis was 4 pages over the limit — she fought for it and won.", "current_status": "Propulsion Engineer at NASA JPL"},
    {"id": 5, "name": "Leo Kim", "nickname": "LK", "photo_url": None, "bio": "Design major who made our group look way cooler than we actually were.", "fun_fact": "Designed the group's unofficial logo during a 3AM coffee run.", "current_status": "UX Designer at Figma"},
    {"id": 6, "name": "Sara Johansson", "nickname": "Saz", "photo_url": None, "bio": "English lit major who wrote everyone's love letters (whether we asked or not).", "fun_fact": "Her poetry slam went viral on campus radio.", "current_status": "Freelance Writer & Editor"},
    {"id": 7, "name": "David Park", "nickname": "DP", "photo_url": None, "bio": "History buff who somehow made every conversation about the Roman Empire.", "fun_fact": "Can recite the Gettysburg Address from memory — backwards.", "current_status": "High School History Teacher"},
    {"id": 8, "name": "Aisha Mohammed", "nickname": "Aish", "photo_url": None, "bio": "Pre-med with a secret talent for stand-up comedy during study breaks.", "fun_fact": "Never pulled an all-nighter — witchcraft, according to the rest of us.", "current_status": "Pediatric Resident at Children's Hospital"},
    {"id": 9, "name": "Tomás Silva", "nickname": "T", "photo_url": None, "bio": "Music major who recorded our group's unofficial anthem in a broom closet.", "fun_fact": "His playlist 'Study Beats 2020' has 2 million streams on Spotify.", "current_status": "Music Producer & Audio Engineer"},
    {"id": 10, "name": "Yuki Tanaka", "nickname": "Yuk", "photo_url": None, "bio": "Architecture student who built a cardboard castle for our final-year party.", "fun_fact": "Speaks four languages, still can't say 'no' to free food.", "current_status": "Junior Architect at SOM Tokyo"},
]


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/our-story", response_class=HTMLResponse)
async def our_story(request: Request):
    return templates.TemplateResponse("story.html", {"request": request})


@router.get("/squad", response_class=HTMLResponse)
async def squad(request: Request):
    return templates.TemplateResponse("squad.html", {"request": request, "members": MEMBERS})


@router.get("/squad/{member_id:int}", response_class=HTMLResponse)
async def member_detail(request: Request, member_id: int):
    member = next((m for m in MEMBERS if m["id"] == member_id), None)
    return templates.TemplateResponse("member_detail.html", {"request": request, "member": member})


@router.get("/timeline", response_class=HTMLResponse)
async def timeline(request: Request):
    years = {}
    for event in TIMELINE_EVENTS:
        years.setdefault(event["year"], []).append(event)
    return templates.TemplateResponse("timeline.html", {"request": request, "years": years})


@router.get("/gallery", response_class=HTMLResponse)
async def gallery(request: Request):
    categories = sorted(set(item["category"] for item in GALLERY_ITEMS))
    return templates.TemplateResponse("gallery.html", {"request": request, "gallery_items": GALLERY_ITEMS, "categories": categories})


@router.get("/updates", response_class=HTMLResponse)
async def updates(request: Request):
    return templates.TemplateResponse("updates.html", {"request": request, "updates": UPDATES})


@router.get("/events", response_class=HTMLResponse)
async def events(request: Request):
    return templates.TemplateResponse("events.html", {"request": request, "events_list": EVENTS_LIST})


@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})
