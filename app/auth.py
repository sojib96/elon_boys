import bcrypt as _bcrypt_mod

if not hasattr(_bcrypt_mod, "__about__"):
    class _BcryptAbout:
        __version__ = _bcrypt_mod.__version__
    _bcrypt_mod.__about__ = _BcryptAbout()

from fastapi import Request
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.database import engine
from app.models import Member

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class NotAuthenticatedException(Exception):
    pass


def get_current_member(request: Request) -> Member:
    """Cookie-session auth for 10 fixed member accounts — not a general-purpose system."""
    member_id = request.session.get("member_id")
    if member_id is None:
        raise NotAuthenticatedException()
    with Session(engine) as session:
        member = session.get(Member, member_id)
    if member is None:
        raise NotAuthenticatedException()
    return member


def get_current_member_optional(request: Request) -> Member | None:
    """Same lookup as get_current_member but returns None instead of raising."""
    member_id = request.session.get("member_id")
    if member_id is None:
        return None
    with Session(engine) as session:
        member = session.get(Member, member_id)
    return member
