import os

from sqlalchemy import text
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/friends.db")

# If using SQLite locally, ensure the parent directory exists
if DATABASE_URL.startswith("sqlite"):
    from pathlib import Path
    db_path = DATABASE_URL.replace("sqlite:///", "")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    _migrate()


def _migrate():
    with Session(engine) as session:
        conn = session.connection()
        for table in ("galleryitem", "updatepost"):
            try:
                conn.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN permanently_hidden INTEGER NOT NULL DEFAULT 0")
                )
            except Exception:
                pass

        member_cols = [
            "phone TEXT",
            "instagram TEXT",
            "github TEXT",
            "linkedin TEXT",
            "portfolio_url TEXT",
            "date_of_birth TEXT",
            "current_city TEXT",
            "gender TEXT",
            "blood_group TEXT",
            "relationship_status TEXT",
            "occupation TEXT",
            "current_company TEXT",
            "quote TEXT",
            "image1 TEXT",
            "image2 TEXT",
            "resume_url TEXT",
        ]
        for col_def in member_cols:
            try:
                conn.execute(text(f"ALTER TABLE member ADD COLUMN {col_def}"))
            except Exception:
                pass
        conn.commit()


def get_session():
    with Session(engine) as session:
        yield session
