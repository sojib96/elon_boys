import re
import secrets
from pathlib import Path

from sqlmodel import Session, select

from app.auth import hash_password
from app.models import GlobalQuestion, Member
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
            photo_url=m.get("photo_url"),
            bio=m.get("bio"),
            fun_fact=m.get("fun_fact"),
            current_status=m.get("current_status"),
            tag=m.get("tag"),
            username=slug,
            hashed_password=hash_password(password),
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
