import re
import secrets
from pathlib import Path

from sqlmodel import Session, select

from app.auth import hash_password
from app.models import GlobalQuestion, GuestbookEntry, Member
from app.routers.public import MEMBERS

CREDENTIALS_FILE = Path(__file__).resolve().parent.parent / "SEEDED_CREDENTIALS.txt"


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", ".", name.lower()).strip(".")
    slug = re.sub(r"\.+", ".", slug)
    return slug


def seed_members(session: Session, write_credentials: bool = True) -> None:
    existing = session.exec(select(Member).limit(1)).first()
    if existing is not None:
        return

    used_slugs: set[str] = set()
    credentials: list[str] = []

    for m in MEMBERS:
        base_slug = _slugify(m["name"])
        slug = base_slug
        counter = 2
        while slug in used_slugs:
            slug = f"{base_slug}{counter}"
            counter += 1
        used_slugs.add(slug)

        password = secrets.token_urlsafe(12)
        member = Member(
            name=m["name"],
            nickname=m["nickname"],
            username=slug,
            hashed_password=hash_password(password),
            email=m.get("email"),
            photo_url=m.get("photo_url"),
            image1=m.get("image1"),
            image2=m.get("image2"),
            bio=m.get("bio"),
            fun_fact=m.get("fun_fact"),
            current_status=m.get("current_status"),
            tag=m.get("tag"),
            quote=m.get("quote"),
        )
        session.add(member)
        credentials.append(f"{slug}  {password}")

    session.commit()

    header = (
        "SEEDED CREDENTIALS - SAVE THESE, THEY WON'T BE SHOWN AGAIN\n"
        + "=" * 60 + "\n"
        + "username  password\n"
        + "-" * 60 + "\n"
    )
    footer = "\n" + "=" * 60

    console_output = header + "\n".join(credentials) + footer
    print("\n" + console_output + "\n")

    if write_credentials:
        CREDENTIALS_FILE.write_text(console_output, encoding="utf-8")
        print(f"Credentials also written to: {CREDENTIALS_FILE}\n")


def seed_questions(session: Session) -> None:
    existing = {q.question for q in session.exec(select(GlobalQuestion)).all()}

    questions = [
        GlobalQuestion(
            question="How many Elons are there in the group?",
            option_a="8",
            option_b="9",
            option_c="10",
            option_d="11",
            correct_answer="d",
        ),
        GlobalQuestion(
            question="what is the bra size of apurba datta?",
            option_a="34",
            option_b="36",
            option_c="42",
            option_d="Don't know but his boobs is bigger then his crush for sure",
            correct_answer="d",
        ),
    ]
    added = 0
    for q in questions:
        if q.question not in existing:
            session.add(q)
            added += 1
    if added:
        session.commit()
    print(f"Seeded {added} new security question(s).")


GUESTBOOK_SEEDS = [
    {"name": "Sarah M.", "message": "This website is such a beautiful idea! The memories you guys have are priceless."},
    {"name": "Prof. Anderson", "message": "So wonderful to see this group still thriving after all these years. You were always my favourite class!"},
    {"name": "Mike R.", "message": "I was your RA in Year 1. You guys were a handful, but you turned out amazing. So proud!"},
    {"name": "Emily T.", "message": "Love the timeline feature — brought back so many memories of our uni days together."},
    {"name": "David's Mom", "message": "You all grew up so well. Thank you for being such good friends to my son."},
    {"name": "Anonymous", "message": "I came here for the photos, stayed for the chaos. 10/10 would Elon again."},
    {"name": "That One Guy", "message": "Whoever designed this site deserves a raise. Or therapy. Probably both."},
    {"name": "Your Local Hater", "message": "This group chat was better when it was just a group chat. Nice site though."},
]


def seed_guestbook(session: Session) -> None:
    existing = session.exec(select(GuestbookEntry).limit(1)).first()
    if existing is not None:
        return
    for g in GUESTBOOK_SEEDS:
        session.add(GuestbookEntry(**g))
    session.commit()
    print(f"Seeded {len(GUESTBOOK_SEEDS)} guestbook entries.")
