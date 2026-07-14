import os
import uuid
from pathlib import Path

from supabase import create_client

from app.jinja import BASE_DIR

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
BUCKET = "uploads"

_supabase = None


def _get_client():
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase


def _guess_ext(content_type: str) -> str:
    if content_type == "image/jpeg":
        return "jpg"
    if content_type == "image/png":
        return "png"
    if content_type == "image/gif":
        return "gif"
    if content_type == "image/webp":
        return "webp"
    if content_type == "application/pdf":
        return "pdf"
    if content_type == "application/msword":
        return "doc"
    if content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return "docx"
    return "jpg"


def upload_file(data: bytes, folder: str, content_type: str = "image/jpeg") -> str:
    ext = _guess_ext(content_type)
    filename = f"{uuid.uuid4().hex}.{ext}"

    if SUPABASE_URL and SUPABASE_KEY:
        remote_path = f"{folder}/{filename}"
        client = _get_client()
        client.storage.from_(BUCKET).upload(
            remote_path,
            data,
            {"content-type": content_type},
        )
        return client.storage.from_(BUCKET).get_public_url(remote_path)

    local_dir = BASE_DIR / "static" / "uploads" / folder
    local_dir.mkdir(parents=True, exist_ok=True)
    dest = local_dir / filename
    dest.write_bytes(data)
    return f"/static/uploads/{folder}/{filename}"
