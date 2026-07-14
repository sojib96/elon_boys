from sqlmodel import Session, col, select

from app.models import GalleryItem


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
        .where(col(GalleryItem.permanently_hidden) == False)
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
    item.permanently_hidden = True
    session.add(item)
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
