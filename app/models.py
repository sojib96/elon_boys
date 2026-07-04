from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    nickname: str
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    fun_fact: Optional[str] = None
    current_status: Optional[str] = None
    username: str = Field(unique=True)
    hashed_password: str


class TimelineEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    title: str
    description: Optional[str] = None
    photo_urls: Optional[str] = None


class GalleryItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str
    file_url: str
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class UpdatePost(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    author: str
    posted_at: datetime = Field(default_factory=datetime.utcnow)


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    date: str
    description: Optional[str] = None
    is_upcoming: bool = True


class GuestbookEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    message: str
    posted_at: datetime = Field(default_factory=datetime.utcnow)


class PrivateUpload(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    file_url: str
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class InternalNote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    author: str
    message: str
    posted_at: datetime = Field(default_factory=datetime.utcnow)
