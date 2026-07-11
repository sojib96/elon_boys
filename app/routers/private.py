import random
import secrets
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from app.auth import (
    get_current_member,
    hash_password,
    verify_password,
)
from app.database import engine, get_session
from app.email_utils import send_email
from app.jinja import BASE_DIR, templates
from app.models import GlobalQuestion, Member
from app.routers.public import MEMBERS
from app.schemas import UpdateCreate, UpdateEdit
from app.services import updates as updates_svc

router = APIRouter()

UPLOADS_DIR = BASE_DIR / "static" / "uploads" / "updates"

MEMBER_NAMES = [m["name"] for m in MEMBERS]

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


# ── Auth routes ──────────────────────────────────────────────────────

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    member_id = request.session.get("member_id")
    if member_id:
        return RedirectResponse("/behind-the-curtain", status_code=303)
    return templates.TemplateResponse(
        "private/login.html",
        {"request": request, "error": None},
    )


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    member_id = request.session.get("member_id")
    if member_id:
        return RedirectResponse("/behind-the-curtain", status_code=303)

    with Session(engine) as session:
        member = session.exec(
            select(Member).where(Member.username == username)
        ).first()

    if member is None or not verify_password(password, member.hashed_password):
        return templates.TemplateResponse(
            "private/login.html",
            {"request": request, "error": "Invalid username or password."},
            status_code=401,
        )

    request.session["member_id"] = member.id
    return RedirectResponse("/behind-the-curtain", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


# ── Forgot password / security question routes ──────────────────────

@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        "private/forgot_password.html",
        {"request": request, "error": None, "success": None, "question": None, "email": None},
    )


@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password_submit(
    request: Request,
    email: str = Form(None),
    question_id: int = Form(None),
    answer: str = Form(None),
):
    with Session(engine) as session:
        if question_id is not None and answer is not None:
            question = session.get(GlobalQuestion, question_id)
            if question is None:
                return templates.TemplateResponse(
                    "private/forgot_password.html",
                    {"request": request, "error": "Invalid question. Please try again.", "success": None, "question": None, "email": None},
                    status_code=400,
                )

            if answer.lower() != question.correct_answer.lower():
                all_questions = session.exec(select(GlobalQuestion)).all()
                if not all_questions:
                    return templates.TemplateResponse(
                        "private/forgot_password.html",
                        {"request": request, "error": "No security questions configured. Contact an admin.", "success": None, "question": None, "email": None},
                    )
                new_question = random.choice(all_questions)
                return templates.TemplateResponse(
                    "private/forgot_password.html",
                    {"request": request, "error": "Incorrect answer. Try again.", "success": None, "question": new_question, "email": None},
                    status_code=400,
                )

            email_from_form = request.session.get("forgot_email")
            if not email_from_form:
                return templates.TemplateResponse(
                    "private/forgot_password.html",
                    {"request": request, "error": "Session expired. Start over.", "success": None, "question": None, "email": None},
                    status_code=400,
                )

            member = session.exec(
                select(Member).where(Member.email == email_from_form)
            ).first()

            if member is None:
                return templates.TemplateResponse(
                    "private/forgot_password.html",
                    {"request": request, "error": "Account not found. Start over.", "success": None, "question": None, "email": None},
                    status_code=400,
                )

            new_password = secrets.token_urlsafe(12)
            member.hashed_password = hash_password(new_password)
            session.add(member)
            session.commit()

            request.session.pop("forgot_email", None)

            body = (
                f"Hey {member.nickname},\n\n"
                f"Look at you, forgetting your password like it's a childhood memory.\n"
                f"Don't worry, we've all been there — some of us more than others.\n\n"
                f"Your brand new password is: {new_password}\n\n"
                f"Write it down this time. Tattoo it on your arm. Whatever works.\n"
                f"And maybe don't share it with the group chat again.\n\n"
                f"Cheers,\nThe Elon Boys Website\n"
                f"(P.S. We're not mad, just disappointed.)"
            )
            send_email(email_from_form, "Elon Boys — Your New Password", body)

            return templates.TemplateResponse(
                "private/forgot_password.html",
                {"request": request, "error": None, "success": "A new password has been sent to your email.", "question": None, "email": None},
            )

        if not email:
            return templates.TemplateResponse(
                "private/forgot_password.html",
                {"request": request, "error": "Please enter your email.", "success": None, "question": None, "email": None},
                status_code=400,
            )

        member = session.exec(
            select(Member).where(Member.email == email)
        ).first()

        if member is None:
            return templates.TemplateResponse(
                "private/forgot_password.html",
                {"request": request, "error": "No account found with that email.", "success": None, "question": None, "email": None},
                status_code=400,
            )

        all_questions = session.exec(select(GlobalQuestion)).all()
        if not all_questions:
            return templates.TemplateResponse(
                "private/forgot_password.html",
                {"request": request, "error": "No security questions configured. Contact an admin.", "success": None, "question": None, "email": None},
            )

        question = random.choice(all_questions)
        request.session["forgot_email"] = email

    return templates.TemplateResponse(
        "private/forgot_password.html",
        {"request": request, "error": None, "success": None, "question": question, "email": email},
    )


# ── Protected private routes ─────────────────────────────────────────

@router.get("/uploads", response_class=HTMLResponse)
async def uploads(request: Request, _auth: Member = Depends(get_current_member)):
    return templates.TemplateResponse(
        "private/uploads.html",
        {"request": request, "uploads": PRIVATE_UPLOADS, "member": _auth},
    )


@router.get("/notes", response_class=HTMLResponse)
async def notes(request: Request, _auth: Member = Depends(get_current_member)):
    return templates.TemplateResponse(
        "private/notes.html",
        {"request": request, "notes_list": INTERNAL_NOTES, "member": _auth},
    )


@router.get("/updates/new", response_class=HTMLResponse)
async def create_update_form(
    request: Request,
    _auth: Member = Depends(get_current_member),
):
    return templates.TemplateResponse(
        "private/create_update.html",
        {"request": request, "authors": MEMBER_NAMES, "errors": {}, "form": {}, "member": _auth},
    )


@router.post("/updates/new", response_class=HTMLResponse)
async def create_update_submit(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    excerpt: str = Form(""),
    author: str = Form(...),
    files: list[UploadFile] = File(default=[]),
    session: Session = Depends(get_session),
    _auth: Member = Depends(get_current_member),
):
    errors = {}
    if not title.strip():
        errors["title"] = "Title is required."
    if not content.strip():
        errors["content"] = "Content is required."
    if not author.strip():
        errors["author"] = "Author is required."

    image_urls = []
    saved_files = []
    for f in files:
        if not f.filename:
            continue
        if not f.content_type or not f.content_type.startswith("image/"):
            errors.setdefault("files", []).append(
                f"'{f.filename}' is not a valid image (received {f.content_type})."
            )
            continue
        ext = Path(f.filename).suffix.lower() if f.filename else ".jpg"
        safe_name = f"{uuid.uuid4().hex}{ext}"
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        dest = UPLOADS_DIR / safe_name
        content_bytes = await f.read()
        dest.write_bytes(content_bytes)
        image_urls.append(f"/static/uploads/updates/{safe_name}")
        saved_files.append(dest)

    if errors:
        return templates.TemplateResponse(
            "private/create_update.html",
            {
                "request": request,
                "authors": MEMBER_NAMES,
                "errors": errors,
                "form": {"title": title, "content": content, "excerpt": excerpt, "author": author},
                "member": _auth,
            },
            status_code=422,
        )

    data = UpdateCreate(
        title=title.strip(),
        content=content.strip(),
        excerpt=excerpt.strip() or None,
        author=author.strip(),
        image_urls=image_urls,
    )
    post = updates_svc.create_update(session, data)
    return RedirectResponse(url=f"/updates/{post.id}", status_code=302)


@router.get("/updates/{update_id:int}/edit", response_class=HTMLResponse)
async def edit_update_form(
    request: Request,
    update_id: int,
    session: Session = Depends(get_session),
    _auth: Member = Depends(get_current_member),
):
    post = updates_svc.get_update(session, update_id)
    if not post:
        raise HTTPException(status_code=404)
    existing_images = [{"id": img.id, "file_url": img.file_url} for img in post.images]
    return templates.TemplateResponse(
        "private/create_update.html",
        {
            "request": request,
            "authors": MEMBER_NAMES,
            "errors": {},
            "form": {
                "title": post.title,
                "content": post.content,
                "excerpt": post.excerpt or "",
                "author": post.author,
            },
            "existing_images": existing_images,
            "post": post,
            "member": _auth,
        },
    )


@router.post("/updates/{update_id:int}/edit", response_class=HTMLResponse)
async def edit_update_submit(
    request: Request,
    update_id: int,
    title: str = Form(...),
    content: str = Form(...),
    excerpt: str = Form(""),
    author: str = Form(...),
    delete_image_ids: list[int] = Form([]),
    files: list[UploadFile] = File(default=[]),
    session: Session = Depends(get_session),
    _auth: Member = Depends(get_current_member),
):
    post = updates_svc.get_update(session, update_id)
    if not post:
        raise HTTPException(status_code=404)

    errors = {}
    if not title.strip():
        errors["title"] = "Title is required."
    if not content.strip():
        errors["content"] = "Content is required."
    if not author.strip():
        errors["author"] = "Author is required."

    new_image_urls = []
    saved_files = []
    for f in files:
        if not f.filename:
            continue
        if not f.content_type or not f.content_type.startswith("image/"):
            errors.setdefault("files", []).append(
                f"'{f.filename}' is not a valid image (received {f.content_type})."
            )
            continue
        ext = Path(f.filename).suffix.lower() if f.filename else ".jpg"
        safe_name = f"{uuid.uuid4().hex}{ext}"
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        dest = UPLOADS_DIR / safe_name
        content_bytes = await f.read()
        dest.write_bytes(content_bytes)
        new_image_urls.append(f"/static/uploads/updates/{safe_name}")
        saved_files.append(dest)

    if errors:
        existing_images = [{"id": img.id, "file_url": img.file_url} for img in post.images]
        return templates.TemplateResponse(
            "private/create_update.html",
            {
                "request": request,
                "authors": MEMBER_NAMES,
                "errors": errors,
                "form": {"title": title, "content": content, "excerpt": excerpt, "author": author},
                "existing_images": existing_images,
                "post": post,
                "member": _auth,
            },
            status_code=422,
        )

    data = UpdateEdit(
        title=title.strip(),
        content=content.strip(),
        excerpt=excerpt.strip() or None,
        author=author.strip(),
        new_image_urls=new_image_urls,
        delete_image_ids=delete_image_ids,
    )
    updated = updates_svc.update_update(session, update_id, data)
    return RedirectResponse(url=f"/updates/{updated.id}", status_code=302)


@router.post("/updates/{update_id:int}/delete")
async def delete_update(
    request: Request,
    update_id: int,
    session: Session = Depends(get_session),
    _auth: Member = Depends(get_current_member),
):
    deleted = updates_svc.delete_update(session, update_id)
    if not deleted:
        raise HTTPException(status_code=404)
    return RedirectResponse(url="/updates", status_code=302)


@router.get("/behind-the-curtain", response_class=HTMLResponse)
async def behind_the_curtain(request: Request, _auth: Member = Depends(get_current_member)):
    return templates.TemplateResponse(
        "private/behind_the_curtain.html",
        {"request": request, "member": _auth},
    )
