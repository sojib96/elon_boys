from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


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
    tag: Optional[str] = None
    email: Optional[str] = None


class GlobalQuestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str  # "a", "b", "c", or "d"


class TimelineEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    title: str
    description: Optional[str] = None
    photo_urls: Optional[str] = None


class GalleryItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    category: str
    file_url: str
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    source_update_id: Optional[int] = Field(default=None, foreign_key="updatepost.id")
    is_deleted: bool = Field(default=False)


class UpdatePost(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    excerpt: Optional[str] = None
    # author is a plain string for now; will become a FK to Member once auth is wired up
    author: str
    posted_at: datetime = Field(default_factory=datetime.utcnow)
    is_deleted: bool = Field(default=False)
    images: list["UpdateImage"] = Relationship(back_populates="update")


class UpdateImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    update_id: int = Field(foreign_key="updatepost.id")
    file_url: str
    alt_text: Optional[str] = None
    order_index: int = Field(default=0)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    is_deleted: bool = Field(default=False)
    update: Optional[UpdatePost] = Relationship(back_populates="images")


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
