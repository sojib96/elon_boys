from datetime import datetime
import math
from pathlib import Path

from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, select

from app.jinja import BASE_DIR
from app.models import GalleryItem, UpdateImage, UpdatePost
from app.schemas import UpdateCreate, UpdateEdit
from app.services.gallery import (
    create_gallery_item,
    delete_gallery_by_update,
    restore_gallery_by_update,
)


def list_updates(session: Session) -> list[UpdatePost]:
    stmt = (
        select(UpdatePost)
        .where(col(UpdatePost.is_deleted) == False)
        .options(selectinload(UpdatePost.images))
        .order_by(col(UpdatePost.posted_at).desc())
    )
    return list(session.exec(stmt).all())


def get_update(session: Session, update_id: int) -> UpdatePost | None:
    stmt = (
        select(UpdatePost)
        .where(UpdatePost.id == update_id)
        .where(col(UpdatePost.is_deleted) == False)
        .options(selectinload(UpdatePost.images))
    )
    return session.exec(stmt).first()


def get_related(session: Session, exclude_id: int, limit: int = 2) -> list[UpdatePost]:
    stmt = (
        select(UpdatePost)
        .where(col(UpdatePost.id) != exclude_id)
        .where(col(UpdatePost.is_deleted) == False)
        .options(selectinload(UpdatePost.images))
        .order_by(col(UpdatePost.posted_at).desc())
        .limit(limit)
    )
    return list(session.exec(stmt).all())


def list_deleted_updates(session: Session, author: str) -> list[UpdatePost]:
    stmt = (
        select(UpdatePost)
        .where(col(UpdatePost.is_deleted) == True)
        .where(col(UpdatePost.permanently_hidden) == False)
        .where(col(UpdatePost.author) == author)
        .options(selectinload(UpdatePost.images))
        .order_by(col(UpdatePost.posted_at).desc())
    )
    return list(session.exec(stmt).all())


HERO_WORD_LIMIT = 60


def _active_images(post: UpdatePost) -> list[UpdateImage]:
    return [img for img in post.images if not img.is_deleted]


def _stagger(paragraphs: list[str], images: list[UpdateImage]) -> list[dict]:
    blocks: list[dict] = []
    p_count = len(paragraphs)
    i_count = len(images)

    if p_count == 0:
        return [{"type": "image", "image": img} for img in images]

    if i_count == 0:
        return [{"type": "text", "content": p} for p in paragraphs]

    if i_count >= p_count:
        for i, p in enumerate(paragraphs):
            blocks.append({"type": "text", "content": p})
            if i < i_count:
                blocks.append({"type": "image", "image": images[i]})
        for extra in images[p_count:]:
            blocks.append({"type": "image", "image": extra})
        return blocks

    step = max(1, math.ceil(p_count / (i_count + 1)))
    insert_positions: set[int] = set()
    for n in range(1, i_count + 1):
        insert_positions.add(min(step * n, p_count))

    img_idx = 0
    for i, p in enumerate(paragraphs, 1):
        blocks.append({"type": "text", "content": p})
        if i in insert_positions and img_idx < i_count:
            blocks.append({"type": "image", "image": images[img_idx]})
            img_idx += 1

    return blocks


def build_content_blocks(
    post: UpdatePost,
) -> tuple[str | None, list[dict]]:
    paragraphs = [p for p in post.content.split("\n") if p.strip()]
    remaining_images = _active_images(post)[1:]

    if not paragraphs:
        return None, _stagger([], remaining_images)

    first = paragraphs[0]
    words = first.split()

    if len(words) <= HERO_WORD_LIMIT:
        hero_intro = first
        body_paragraphs = paragraphs[1:]
    else:
        hero_intro = " ".join(words[:HERO_WORD_LIMIT]) + "..."
        body_paragraphs = [" ".join(words[HERO_WORD_LIMIT:])] + paragraphs[1:]

    blocks = _stagger(body_paragraphs, remaining_images)
    return hero_intro, blocks


def create_update(session: Session, data: UpdateCreate) -> UpdatePost:
    post = UpdatePost(
        title=data.title,
        content=data.content,
        excerpt=data.excerpt,
        author=data.author,
    )
    session.add(post)
    session.flush()
    for idx, url in enumerate(data.image_urls):
        session.add(UpdateImage(update_id=post.id, file_url=url, order_index=idx))
        create_gallery_item(
            session,
            title=f"{data.title} — Photo {idx + 1}",
            category="Updates",
            file_url=url,
            uploaded_by=data.author,
            source_update_id=post.id,
        )
    session.commit()
    session.refresh(post)
    return post


def update_update(session: Session, update_id: int, data: UpdateEdit) -> UpdatePost | None:
    post = get_update(session, update_id)
    if not post:
        return None
    post.title = data.title
    post.content = data.content
    post.excerpt = data.excerpt
    post.author = data.author
    if data.delete_image_ids:
        deleted_images = session.exec(
            select(UpdateImage).where(
                col(UpdateImage.id).in_(data.delete_image_ids),
                UpdateImage.update_id == update_id,
            )
        ).all()
        deleted_urls = {img.file_url for img in deleted_images}
        for img in deleted_images:
            img.is_deleted = True
            session.add(img)
        gallery_to_delete = session.exec(
            select(GalleryItem).where(
                col(GalleryItem.source_update_id) == update_id,
                col(GalleryItem.file_url).in_(deleted_urls),
            )
        ).all()
        for g in gallery_to_delete:
            g.is_deleted = True
            session.add(g)
    session.flush()
    max_order = 0
    existing = session.exec(
        select(UpdateImage)
        .where(UpdateImage.update_id == update_id)
        .where(col(UpdateImage.is_deleted) == False)
        .order_by(col(UpdateImage.order_index).desc())
    ).all()
    if existing:
        max_order = existing[0].order_index + 1
    for idx, url in enumerate(data.new_image_urls):
        session.add(UpdateImage(update_id=post.id, file_url=url, order_index=max_order + idx))
        create_gallery_item(
            session,
            title=f"{data.title} — Photo {max_order + idx + 1}",
            category="Updates",
            file_url=url,
            uploaded_by=data.author,
            source_update_id=update_id,
        )
    session.commit()
    session.refresh(post)
    return post


def delete_update(session: Session, update_id: int) -> bool:
    post = session.get(UpdatePost, update_id)
    if not post:
        return False
    post.is_deleted = True
    session.add(post)
    images = session.exec(
        select(UpdateImage).where(UpdateImage.update_id == update_id)
    ).all()
    for img in images:
        img.is_deleted = True
        session.add(img)
    delete_gallery_by_update(session, update_id)
    session.commit()
    return True


def restore_update(session: Session, update_id: int) -> bool:
    post = session.get(UpdatePost, update_id)
    if not post:
        return False
    post.is_deleted = False
    session.add(post)
    images = session.exec(
        select(UpdateImage).where(UpdateImage.update_id == update_id)
    ).all()
    for img in images:
        img.is_deleted = False
        session.add(img)
    restore_gallery_by_update(session, update_id)
    session.commit()
    return True


def permanent_delete_update(session: Session, update_id: int) -> bool:
    post = session.get(UpdatePost, update_id)
    if not post:
        return False
    post.permanently_hidden = True
    session.add(post)
    session.commit()
    return True


def seed_if_empty(session: Session) -> None:
    existing = session.exec(select(UpdatePost).limit(1)).first()
    if existing is not None:
        return

    seeds = [
        {
            "title": "Five Years Since Graduation",
            "content": "Can you believe it's been five years? We're planning a reunion this summer. Details coming soon — save the date for August 15th!",
            "excerpt": "Reunion plans are underway for August 15th.",
            "author": "Md Sojib",
            "posted_at": datetime(2026, 6, 15),
        },
        {
            "title": "Welcome to the Website!",
            "content": "We finally have a permanent home for all our memories. This is where we'll keep our photos, stories, and updates. Welcome back, everyone.",
            "excerpt": "Our permanent home for photos, stories, and updates.",
            "author": "Md. Nazmul Islam Nayem",
            "posted_at": datetime(2026, 6, 1),
        },
        {
            "title": "New Addition to the Squad",
            "content": "Big news — Mehedi and his partner just welcomed a baby girl! Little Sofia already has the whole group wrapped around her finger. Mazel tov!",
            "excerpt": "Mehedi welcomed a baby girl named Sofia!",
            "author": "Md. Mehedi Hasan",
            "posted_at": datetime(2026, 5, 20),
        },
        {
            "title": "Farhan Dropped a New Track",
            "content": "Our very own music producer just released a new single. It's called 'Nostalgia' and yes, there's a sample of our graduation night in there. Go stream it!",
            "excerpt": "Farhan released a new single called 'Nostalgia'.",
            "author": "Farhan Jarif Nibir",
            "posted_at": datetime(2026, 4, 10),
        },
        {
            "title": "Remembering the House",
            "content": "Niaz found a video from our old house share. It's 3 minutes of chaos, burnt toast, and someone falling off a chair. It's perfect.",
            "excerpt": "A found video from the old house share days.",
            "author": "Niaz Mahmud",
            "posted_at": datetime(2026, 3, 5),
        },
        {
            "title": "Beach Day Flashback",
            "content": "Remember when we spent an entire Saturday building a sandcastle that looked more like a sand-blob? Best Worst Castle 2023, right there.",
            "excerpt": "Our legendary sand-blob from 2023.",
            "author": "Al Zubayer Saad",
            "posted_at": datetime(2026, 2, 18),
        },
        {
            "title": "The Great Pancake Disaster",
            "content": "Someone (Arnob) thought it was a good idea to flip pancakes without a spatula. The ceiling still has a stain. We framed it as modern art.",
            "excerpt": "Arnob's spatula-free pancake experiment gone wrong.",
            "author": "Safi Ullah Chowdhury",
            "posted_at": datetime(2026, 1, 22),
        },
        {
            "title": "Midnight Rooftop Conversations",
            "content": "Some of the best talks happened on that creaky rooftop. Life, love, dreams, and whether pineapple belongs on pizza. The jury's still out.",
            "excerpt": "Late-night talks on the creaky rooftop.",
            "author": "Apurba Datta",
            "posted_at": datetime(2025, 12, 14),
        },
    ]

    for s in seeds:
        post = UpdatePost(
            title=s["title"],
            content=s["content"],
            excerpt=s["excerpt"],
            author=s["author"],
            posted_at=s["posted_at"],
        )
        session.add(post)
    session.commit()
