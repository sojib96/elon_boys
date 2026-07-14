import random
import secrets
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
from app.image_utils import process_avatar, process_cover, process_gallery, process_squad_card, process_update_image
from app.jinja import templates
from app.models import GalleryItem, GlobalQuestion, InternalNote, Member, UpdatePost
from app.schemas import UpdateCreate, UpdateEdit
from app.services import gallery as gallery_svc
from app.services import updates as updates_svc
from app.storage import upload_file

router = APIRouter()

PRIVATE_UPLOADS = [
    {"id": 1, "file_url": None, "title": "Graduation video (raw)", "uploaded_by": "Alex", "uploaded_at": "2026-06-20"},
    {"id": 2, "file_url": None, "title": "Road trip blooper reel", "uploaded_by": "Maya", "uploaded_at": "2026-06-18"},
    {"id": 3, "file_url": None, "title": "House party photos", "uploaded_by": "James", "uploaded_at": "2026-06-15"},
    {"id": 4, "file_url": None, "title": "Secret Santa outtakes", "uploaded_by": "Priya", "uploaded_at": "2026-06-10"},
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
    identifier: str = Form(...),
    password: str = Form(...),
):
    member_id = request.session.get("member_id")
    if member_id:
        return RedirectResponse("/behind-the-curtain", status_code=303)

    with Session(engine) as session:
        member = session.exec(
            select(Member).where(Member.username == identifier)
        ).first()
        if member is None:
            member = session.exec(
                select(Member).where(Member.email == identifier)
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
async def notes(
    request: Request,
    session: Session = Depends(get_session),
    _auth: Member = Depends(get_current_member),
):
    notes_list = session.exec(
        select(InternalNote).order_by(InternalNote.posted_at.desc())
    ).all()
    return templates.TemplateResponse(
        "private/notes.html",
        {"request": request, "notes_list": notes_list, "member": _auth},
    )


@router.post("/notes", response_class=HTMLResponse)
async def notes_post(
    request: Request,
    message: str = Form(min_length=1),
    session: Session = Depends(get_session),
    _auth: Member = Depends(get_current_member),
):
    note = InternalNote(author=_auth.name, message=message.strip())
    session.add(note)
    session.commit()
    return RedirectResponse(url="/notes", status_code=303)


@router.get("/updates/new", response_class=HTMLResponse)
async def create_update_form(
    request: Request,
    _auth: Member = Depends(get_current_member),
):
    return templates.TemplateResponse(
        "private/create_update.html",
        {"request": request, "authors": [], "errors": {}, "form": {}, "member": _auth},
    )


@router.post("/updates/new", response_class=HTMLResponse)
async def create_update_submit(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    excerpt: str = Form(""),
    files: list[UploadFile] = File(default=[]),
    session: Session = Depends(get_session),
    _auth: Member = Depends(get_current_member),
):
    errors = {}
    if not title.strip():
        errors["title"] = "Title is required."
    if not content.strip():
        errors["content"] = "Content is required."

    image_urls = []
    for f in files:
        if not f.filename:
            continue
        if not f.content_type or not f.content_type.startswith("image/"):
            errors.setdefault("files", []).append(
                f"'{f.filename}' is not a valid image (received {f.content_type})."
            )
            continue
        content_bytes = await f.read()
        processed = process_update_image(content_bytes)
        image_urls.append(upload_file(processed, "updates", "image/jpeg"))

    if errors:
        return templates.TemplateResponse(
            "private/create_update.html",
            {
                "request": request,
                "authors": [],
                "errors": errors,
                "form": {"title": title, "content": content, "excerpt": excerpt},
                "member": _auth,
            },
            status_code=422,
        )

    data = UpdateCreate(
        title=title.strip(),
        content=content.strip(),
        excerpt=excerpt.strip() or None,
        author=_auth.name,
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
    if post.author != _auth.name:
        raise HTTPException(status_code=403)
    existing_images = [{"id": img.id, "file_url": img.file_url} for img in post.images if not img.is_deleted]
    return templates.TemplateResponse(
        "private/create_update.html",
        {
            "request": request,
            "authors": [],
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
    delete_image_ids: list[int] = Form([]),
    files: list[UploadFile] = File(default=[]),
    session: Session = Depends(get_session),
    _auth: Member = Depends(get_current_member),
):
    post = updates_svc.get_update(session, update_id)
    if not post:
        raise HTTPException(status_code=404)
    if post.author != _auth.name:
        raise HTTPException(status_code=403)

    errors = {}
    if not title.strip():
        errors["title"] = "Title is required."
    if not content.strip():
        errors["content"] = "Content is required."

    new_image_urls = []
    for f in files:
        if not f.filename:
            continue
        if not f.content_type or not f.content_type.startswith("image/"):
            errors.setdefault("files", []).append(
                f"'{f.filename}' is not a valid image (received {f.content_type})."
            )
            continue
        content_bytes = await f.read()
        processed = process_update_image(content_bytes)
        new_image_urls.append(upload_file(processed, "updates", "image/jpeg"))

    if errors:
        existing_images = [{"id": img.id, "file_url": img.file_url} for img in post.images]
        return templates.TemplateResponse(
            "private/create_update.html",
            {
                "request": request,
                "authors": [],
                "errors": errors,
                "form": {"title": title, "content": content, "excerpt": excerpt},
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
        author=_auth.name,
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
    post = session.get(UpdatePost, update_id)
    if not post:
        raise HTTPException(status_code=404)
    if post.author != _auth.name:
        raise HTTPException(status_code=403)
    deleted = updates_svc.delete_update(session, update_id)
    if not deleted:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        "private/delete_success.html",
        {"request": request, "member": _auth, "post_title": post.title},
    )


@router.get("/gallery/upload", response_class=HTMLResponse)
async def gallery_upload_form(
    request: Request,
    _auth: Member = Depends(get_current_member),
    session: Session = Depends(get_session),
):
    existing = session.exec(select(GalleryItem.category).distinct()).all()
    all_categories = sorted(set(["Events", "Trips", "Campus Life", "Random"] + list(existing)))
    return templates.TemplateResponse(
        "private/upload_gallery.html",
        {"request": request, "member": _auth, "errors": {}, "form": {}, "categories": all_categories},
    )


@router.post("/gallery/upload", response_class=HTMLResponse)
async def gallery_upload_submit(
    request: Request,
    title: str = Form(...),
    category: str = Form(...),
    files: list[UploadFile] = File(default=[]),
    session: Session = Depends(get_session),
    _auth: Member = Depends(get_current_member),
):
    errors = {}
    if not title.strip():
        errors["title"] = "Title is required."
    if not category.strip():
        errors["category"] = "Category is required."
    if not files or not any(f.filename for f in files):
        errors["files"] = "At least one image is required."

    if errors:
        return templates.TemplateResponse(
            "private/upload_gallery.html",
            {
                "request": request,
                "member": _auth,
                "errors": errors,
                "form": {"title": title, "category": category},
            },
            status_code=422,
        )

    valid_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    for f in files:
        if not f.filename:
            continue
        ext = Path(f.filename).suffix.lower() if f.filename else ".jpg"
        if ext not in valid_exts:
            continue
        content_bytes = await f.read()
        processed = process_gallery(content_bytes)
        file_url = upload_file(processed, "gallery", "image/jpeg")
        gallery_svc.create_gallery_item(session, title=title.strip(), category=category, file_url=file_url, uploaded_by=_auth.name)

    return RedirectResponse(url="/gallery", status_code=302)


@router.post("/gallery/{item_id:int}/delete")
async def gallery_delete(
    request: Request,
    item_id: int,
    session: Session = Depends(get_session),
    _auth: Member = Depends(get_current_member),
):
    item = session.get(GalleryItem, item_id)
    if not item:
        raise HTTPException(status_code=404)
    if item.uploaded_by != _auth.name:
        raise HTTPException(status_code=403)
    deleted = gallery_svc.delete_gallery_item(session, item_id)
    if not deleted:
        raise HTTPException(status_code=404)
    return RedirectResponse(url="/gallery", status_code=302)


@router.get("/trash", response_class=HTMLResponse)
async def trash_page(request: Request, session: Session = Depends(get_session), _auth: Member = Depends(get_current_member)):
    deleted_gallery = gallery_svc.list_deleted_gallery(session, _auth.name)
    deleted_updates = updates_svc.list_deleted_updates(session, _auth.name)
    return templates.TemplateResponse(
        "private/trash.html",
        {
            "request": request,
            "member": _auth,
            "deleted_gallery": deleted_gallery,
            "deleted_updates": deleted_updates,
        },
    )


@router.post("/gallery/{item_id:int}/restore")
async def gallery_restore(
    request: Request,
    item_id: int,
    session: Session = Depends(get_session),
    _auth: Member = Depends(get_current_member),
):
    item = session.get(GalleryItem, item_id)
    if not item:
        raise HTTPException(status_code=404)
    if item.uploaded_by != _auth.name:
        raise HTTPException(status_code=403)
    restored = gallery_svc.restore_gallery_item(session, item_id)
    if not restored:
        raise HTTPException(status_code=404)
    return RedirectResponse(url="/trash", status_code=302)


@router.post("/gallery/{item_id:int}/permanent-delete")
async def gallery_permanent_delete(
    request: Request,
    item_id: int,
    session: Session = Depends(get_session),
    _auth: Member = Depends(get_current_member),
):
    item = session.get(GalleryItem, item_id)
    if not item:
        raise HTTPException(status_code=404)
    if item.uploaded_by != _auth.name:
        raise HTTPException(status_code=403)
    deleted = gallery_svc.permanent_delete_gallery_item(session, item_id)
    if not deleted:
        raise HTTPException(status_code=404)
    return RedirectResponse(url="/trash", status_code=302)


@router.post("/updates/{update_id:int}/restore")
async def update_restore(
    request: Request,
    update_id: int,
    session: Session = Depends(get_session),
    _auth: Member = Depends(get_current_member),
):
    post = session.get(UpdatePost, update_id)
    if not post:
        raise HTTPException(status_code=404)
    if post.author != _auth.name:
        raise HTTPException(status_code=403)
    restored = updates_svc.restore_update(session, update_id)
    if not restored:
        raise HTTPException(status_code=404)
    return RedirectResponse(url="/trash", status_code=302)


@router.post("/updates/{update_id:int}/permanent-delete")
async def update_permanent_delete(
    request: Request,
    update_id: int,
    session: Session = Depends(get_session),
    _auth: Member = Depends(get_current_member),
):
    post = session.get(UpdatePost, update_id)
    if not post:
        raise HTTPException(status_code=404)
    if post.author != _auth.name:
        raise HTTPException(status_code=403)
    deleted = updates_svc.permanent_delete_update(session, update_id)
    if not deleted:
        raise HTTPException(status_code=404)
    return RedirectResponse(url="/trash", status_code=302)


@router.get("/profile/edit", response_class=HTMLResponse)
async def edit_profile_form(request: Request, _auth: Member = Depends(get_current_member)):
    return templates.TemplateResponse(
        "private/edit_profile.html",
        {"request": request, "member": _auth, "errors": {}},
    )


@router.post("/profile/edit", response_class=HTMLResponse)
async def edit_profile_submit(
    request: Request,
    nickname: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    instagram: str = Form(""),
    github: str = Form(""),
    linkedin: str = Form(""),
    portfolio_url: str = Form(""),
    date_of_birth: str = Form(""),
    current_city: str = Form(""),
    gender: str = Form(""),
    blood_group: str = Form(""),
    relationship_status: str = Form(""),
    occupation: str = Form(""),
    current_company: str = Form(""),
    current_status: str = Form(""),
    tag: str = Form(""),
    quote: str = Form(""),
    bio: str = Form(""),
    fun_fact: str = Form(""),
    photo: UploadFile = File(None),
    image1: UploadFile = File(None),
    image2: UploadFile = File(None),
    resume: UploadFile = File(None),
    session: Session = Depends(get_session),
    _auth: Member = Depends(get_current_member),
):
    member = session.get(Member, _auth.id)
    if not member:
        raise HTTPException(status_code=404)

    member.nickname = nickname
    member.email = email or None
    member.phone = phone or None
    member.instagram = instagram or None
    member.github = github or None
    member.linkedin = linkedin or None
    member.portfolio_url = portfolio_url or None
    member.date_of_birth = date_of_birth or None
    member.current_city = current_city or None
    member.gender = gender or None
    member.blood_group = blood_group or None
    member.relationship_status = relationship_status or None
    member.occupation = occupation or None
    member.current_company = current_company or None
    member.current_status = current_status or None
    member.tag = tag or None
    member.quote = quote or None
    member.bio = bio or None
    member.fun_fact = fun_fact or None

    def _save_upload(upload: UploadFile, folder: str, process_fn=None) -> str | None:
        if not upload or not upload.filename:
            return None
        content = upload.file.read()
        ct = upload.content_type or "image/jpeg"
        if process_fn:
            content = process_fn(content)
            ct = "image/jpeg"
        return upload_file(content, folder, ct)

    if photo and photo.filename:
        member.photo_url = _save_upload(photo, "members/photos", process_avatar)
    if image1 and image1.filename:
        member.image1 = _save_upload(image1, "members/photos", process_squad_card)
    if image2 and image2.filename:
        member.image2 = _save_upload(image2, "members/photos", process_cover)
    if resume and resume.filename:
        member.resume_url = _save_upload(resume, "members/resumes")

    session.add(member)
    session.commit()

    return RedirectResponse(url="/behind-the-curtain", status_code=302)


@router.get("/behind-the-curtain", response_class=HTMLResponse)
async def behind_the_curtain(request: Request, _auth: Member = Depends(get_current_member)):
    return templates.TemplateResponse(
        "private/behind_the_curtain.html",
        {"request": request, "member": _auth},
    )
