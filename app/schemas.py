from typing import Optional

from pydantic import BaseModel


class UpdateCreate(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    author: str
    image_urls: list[str] = []


class UpdateEdit(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    author: str
    new_image_urls: list[str] = []
    delete_image_ids: list[int] = []


class GuestbookCreate(BaseModel):
    name: str
    message: str
