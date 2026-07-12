from datetime import datetime
from pathlib import Path

from sqlmodel import Session, col, select

from app.jinja import BASE_DIR
from app.models import GalleryItem

UPLOADS_DIR = BASE_DIR / "static" / "uploads" / "gallery"


def _default_seed_items():
    items = [
        {"id": 1, "category": "Events", "title": "Farewell Party 2024", "uploaded_by": "Alex"},
        {"id": 2, "category": "Trips", "title": "Beach Road Trip", "uploaded_by": "Maya"},
        {"id": 3, "category": "Campus Life", "title": "Library Shenanigans", "uploaded_by": "James"},
        {"id": 4, "category": "Events", "title": "Birthday Surprise", "uploaded_by": "Priya"},
        {"id": 5, "category": "Trips", "title": "Mountain Hike", "uploaded_by": "Leo"},
        {"id": 6, "category": "Random", "title": "Late Night Pizza", "uploaded_by": "Sara"},
        {"id": 7, "category": "Campus Life", "title": "Exam Week Madness", "uploaded_by": "David"},
        {"id": 8, "category": "Events", "title": "Festival Stall", "uploaded_by": "Aisha"},
        {"id": 9, "category": "Trips", "title": "Weekend Camping", "uploaded_by": "Tomás"},
        {"id": 10, "category": "Random", "title": "Group Selfie Collection", "uploaded_by": "Yuki"},
        {"id": 11, "category": "Events", "title": "Graduation Ceremony", "uploaded_by": "Alex"},
        {"id": 12, "category": "Campus Life", "title": "Dorm Room Chronicles", "uploaded_by": "Maya"},
        {"id": 13, "category": "Events", "title": "Halloween Costume Party", "uploaded_by": "Tomás"},
        {"id": 14, "category": "Trips", "title": "Sunrise Hike", "uploaded_by": "Leo"},
        {"id": 15, "category": "Random", "title": "Kitchen Dance Party", "uploaded_by": "Sara"},
        {"id": 16, "category": "Campus Life", "title": "Snow Day Fights", "uploaded_by": "Aisha"},
        {"id": 17, "category": "Events", "title": "Secret Santa 2022", "uploaded_by": "David"},
        {"id": 18, "category": "Trips", "title": "Lake House Weekend", "uploaded_by": "Yuki"},
    ]
    valid_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    skip = {"IMG_20200902_125947.jpg"}
    uploads_dir = BASE_DIR / "static" / "uploads"
    uploads = sorted(
        f.name for f in uploads_dir.iterdir()
        if f.suffix.lower() in valid_exts and not f.name.startswith(".") and f.name not in skip
    )
    return items, uploads


def seed_gallery_if_empty(session: Session) -> None:
    existing = session.exec(select(GalleryItem).limit(1)).first()
    if existing is not None:
        return

    items, uploads = _default_seed_items()
    for i, item in enumerate(items):
        photo_url = f"/static/uploads/{uploads[i % len(uploads)]}" if uploads else None
        session.add(GalleryItem(
            title=item["title"],
            category=item["category"],
            file_url=photo_url or "",
            uploaded_by=item["uploaded_by"],
            uploaded_at=datetime(2024, 6, 1),
        ))
    session.commit()


def list_gallery(
    session: Session,
    category: str | None = None,
    sort_by: str = "newest",
    offset: int = 0,
    limit: int = 0,
) -> tuple[list[GalleryItem], int]:
    query = select(GalleryItem).where(col(GalleryItem.is_deleted) == False)

    if category:
        query = query.where(col(GalleryItem.category) == category)

    total = len(session.exec(query).all())

    if sort_by == "oldest":
        query = query.order_by(col(GalleryItem.uploaded_at).asc())
    elif sort_by == "alpha":
        query = query.order_by(col(GalleryItem.title).asc())
    else:
        query = query.order_by(col(GalleryItem.uploaded_at).desc())

    if limit > 0:
        query = query.offset(offset).limit(limit)
    items = list(session.exec(query).all())
    return items, total


def list_deleted_gallery(session: Session, uploaded_by: str) -> list[GalleryItem]:
    query = (
        select(GalleryItem)
        .where(col(GalleryItem.is_deleted) == True)
        .where(col(GalleryItem.uploaded_by) == uploaded_by)
        .order_by(col(GalleryItem.uploaded_at).desc())
    )
    return list(session.exec(query).all())


def create_gallery_item(
    session: Session,
    title: str,
    category: str,
    file_url: str,
    uploaded_by: str,
    source_update_id: int | None = None,
) -> GalleryItem:
    item = GalleryItem(
        title=title,
        category=category,
        file_url=file_url,
        uploaded_by=uploaded_by,
        source_update_id=source_update_id,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_gallery_item(session: Session, item_id: int) -> GalleryItem | None:
    item = session.get(GalleryItem, item_id)
    if not item:
        return None
    item.is_deleted = True
    session.add(item)
    session.commit()
    return item


def restore_gallery_item(session: Session, item_id: int) -> GalleryItem | None:
    item = session.get(GalleryItem, item_id)
    if not item:
        return None
    item.is_deleted = False
    session.add(item)
    session.commit()
    return item


def permanent_delete_gallery_item(session: Session, item_id: int) -> GalleryItem | None:
    item = session.get(GalleryItem, item_id)
    if not item:
        return None
    file_path = BASE_DIR / item.file_url.lstrip("/")
    if file_path.exists() and file_path.is_file():
        file_path.unlink()
    session.delete(item)
    session.commit()
    return item


def delete_gallery_by_update(session: Session, update_id: int) -> None:
    items = session.exec(
        select(GalleryItem).where(col(GalleryItem.source_update_id) == update_id)
    ).all()
    for item in items:
        item.is_deleted = True
        session.add(item)
    session.commit()


def restore_gallery_by_update(session: Session, update_id: int) -> None:
    items = session.exec(
        select(GalleryItem).where(col(GalleryItem.source_update_id) == update_id)
    ).all()
    for item in items:
        item.is_deleted = False
        session.add(item)
    session.commit()
