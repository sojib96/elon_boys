from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from app.database import get_session
from app.jinja import templates
from app.models import GuestbookEntry

router = APIRouter()


@router.get("/guestbook", response_class=HTMLResponse)
async def guestbook_page(request: Request, session: Session = Depends(get_session)):
    entries = session.exec(
        select(GuestbookEntry)
        .order_by(GuestbookEntry.posted_at.desc())
    ).all()

    submitted = request.query_params.get("submitted") == "1"

    return templates.TemplateResponse("guestbook.html", {
        "request": request,
        "entries": entries,
        "submitted": submitted,
    })


@router.post("/guestbook")
async def guestbook_post(
    request: Request,
    name: str = Form(min_length=1),
    message: str = Form(min_length=1),
    session: Session = Depends(get_session),
):
    entry = GuestbookEntry(name=name.strip(), message=message.strip())
    session.add(entry)
    session.commit()
    return RedirectResponse(url="/guestbook?submitted=1", status_code=303)
