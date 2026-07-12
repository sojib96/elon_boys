from datetime import datetime

import pytest
from sqlmodel import Session, SQLModel, create_engine

from app.models import UpdateImage, UpdatePost
from app.schemas import UpdateCreate, UpdateEdit
from app.services.updates import (
    build_content_blocks,
    create_update,
    delete_update,
    get_related,
    get_update,
    list_updates,
    seed_if_empty,
    update_update,
)

TEST_DB_URL = "sqlite:///./data/test_updates.db"
test_engine = create_engine(TEST_DB_URL, echo=False)


@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


class TestListUpdates:
    def test_returns_posts_newest_first(self, setup_db):
        session = setup_db
        session.add(UpdatePost(title="Old", content="c", author="A", posted_at=datetime(2025, 1, 1)))
        session.add(UpdatePost(title="New", content="c", author="A", posted_at=datetime(2026, 6, 1)))
        session.commit()

        posts = list_updates(session)
        assert len(posts) == 2
        assert posts[0].title == "New"
        assert posts[1].title == "Old"

    def test_returns_empty_list_when_no_posts(self, setup_db):
        assert list_updates(setup_db) == []


class TestGetUpdate:
    def test_returns_post_by_id(self, setup_db):
        session = setup_db
        post = UpdatePost(title="Test", content="body", author="A")
        session.add(post)
        session.commit()
        session.refresh(post)

        result = get_update(session, post.id)
        assert result is not None
        assert result.title == "Test"

    def test_returns_none_for_missing_id(self, setup_db):
        assert get_update(setup_db, 999) is None

    def test_includes_images(self, setup_db):
        session = setup_db
        post = UpdatePost(title="With Images", content="body", author="A")
        session.add(post)
        session.flush()
        session.add(UpdateImage(update_id=post.id, file_url="/img/1.jpg", order_index=0))
        session.add(UpdateImage(update_id=post.id, file_url="/img/2.jpg", order_index=1))
        session.commit()

        result = get_update(session, post.id)
        assert len(result.images) == 2
        assert result.images[0].file_url == "/img/1.jpg"
        assert result.images[1].file_url == "/img/2.jpg"


class TestGetRelated:
    def test_excludes_given_id(self, setup_db):
        session = setup_db
        p1 = UpdatePost(title="A", content="c", author="A", posted_at=datetime(2026, 1, 1))
        p2 = UpdatePost(title="B", content="c", author="A", posted_at=datetime(2026, 2, 1))
        p3 = UpdatePost(title="C", content="c", author="A", posted_at=datetime(2026, 3, 1))
        session.add_all([p1, p2, p3])
        session.commit()

        related = get_related(session, exclude_id=p1.id, limit=2)
        ids = [r.id for r in related]
        assert p1.id not in ids
        assert len(related) == 2

    def test_respects_limit(self, setup_db):
        session = setup_db
        for i in range(5):
            session.add(UpdatePost(title=f"P{i}", content="c", author="A"))
        session.commit()

        all_posts = list_updates(session)
        related = get_related(session, exclude_id=all_posts[0].id, limit=2)
        assert len(related) == 2


class TestSeedIfEmpty:
    def test_seeds_when_empty(self, setup_db):
        seed_if_empty(setup_db)
        posts = list_updates(setup_db)
        assert len(posts) == 8

    def test_does_not_duplicate_on_second_call(self, setup_db):
        seed_if_empty(setup_db)
        seed_if_empty(setup_db)
        posts = list_updates(setup_db)
        assert len(posts) == 8

    def test_does_not_overwrite_existing_data(self, setup_db):
        session = setup_db
        session.add(UpdatePost(title="Manual", content="c", author="A"))
        session.commit()

        seed_if_empty(session)
        posts = list_updates(session)
        assert len(posts) == 1
        assert posts[0].title == "Manual"

    def test_seeded_posts_have_images(self, setup_db):
        seed_if_empty(setup_db)
        post = get_update(setup_db, 1)
        assert len(post.images) == 1
        assert post.images[0].file_url.startswith("https://picsum.photos/")

    def test_seeded_posts_ordered_newest_first(self, setup_db):
        seed_if_empty(setup_db)
        posts = list_updates(setup_db)
        dates = [p.posted_at for p in posts]
        assert dates == sorted(dates, reverse=True)


class TestCreateUpdate:
    def test_creates_post_and_images(self, setup_db):
        data = UpdateCreate(
            title="New Post",
            content="Some content",
            excerpt="Short summary",
            author="Test Author",
            image_urls=["/img/a.jpg", "/img/b.jpg"],
        )
        post = create_update(setup_db, data)

        assert post.id is not None
        assert post.title == "New Post"
        assert post.excerpt == "Short summary"
        assert len(post.images) == 2
        assert post.images[0].file_url == "/img/a.jpg"
        assert post.images[0].order_index == 0
        assert post.images[1].file_url == "/img/b.jpg"
        assert post.images[1].order_index == 1

    def test_creates_post_without_images(self, setup_db):
        data = UpdateCreate(
            title="No Images",
            content="Content",
            author="Author",
        )
        post = create_update(setup_db, data)
        assert len(post.images) == 0


class TestUpdateUpdate:
    def test_updates_post_fields(self, setup_db):
        session = setup_db
        post = UpdatePost(title="Old Title", content="Old content", author="Author A")
        session.add(post)
        session.commit()
        session.refresh(post)

        data = UpdateEdit(
            title="New Title",
            content="New content",
            excerpt="Updated excerpt",
            author="Author B",
            new_image_urls=[],
            delete_image_ids=[],
        )
        updated = update_update(session, post.id, data)

        assert updated is not None
        assert updated.title == "New Title"
        assert updated.content == "New content"
        assert updated.excerpt == "Updated excerpt"
        assert updated.author == "Author B"

    def test_returns_none_for_missing_id(self, setup_db):
        data = UpdateEdit(title="T", content="C", author="A")
        assert update_update(setup_db, 999, data) is None

    def test_adds_new_images(self, setup_db):
        session = setup_db
        post = UpdatePost(title="T", content="C", author="A")
        session.add(post)
        session.commit()
        session.refresh(post)

        data = UpdateEdit(
            title="T", content="C", author="A",
            new_image_urls=["/img/new1.jpg", "/img/new2.jpg"],
            delete_image_ids=[],
        )
        updated = update_update(session, post.id, data)
        assert len(updated.images) == 2
        assert updated.images[0].file_url == "/img/new1.jpg"
        assert updated.images[1].file_url == "/img/new2.jpg"

    def test_deletes_marked_images(self, setup_db):
        session = setup_db
        post = UpdatePost(title="T", content="C", author="A")
        session.add(post)
        session.flush()
        img1 = UpdateImage(update_id=post.id, file_url="/img/1.jpg", order_index=0)
        img2 = UpdateImage(update_id=post.id, file_url="/img/2.jpg", order_index=1)
        session.add_all([img1, img2])
        session.commit()
        session.refresh(post)

        data = UpdateEdit(
            title="T", content="C", author="A",
            new_image_urls=[],
            delete_image_ids=[img1.id],
        )
        updated = update_update(session, post.id, data)
        active_images = [img for img in updated.images if not img.is_deleted]
        assert len(active_images) == 1
        assert active_images[0].file_url == "/img/2.jpg"
        assert any(img.id == img1.id and img.is_deleted for img in updated.images)

    def test_deletes_old_and_adds_new_images(self, setup_db):
        session = setup_db
        post = UpdatePost(title="T", content="C", author="A")
        session.add(post)
        session.flush()
        img1 = UpdateImage(update_id=post.id, file_url="/img/old.jpg", order_index=0)
        session.add(img1)
        session.commit()
        session.refresh(post)

        data = UpdateEdit(
            title="T", content="C", author="A",
            new_image_urls=["/img/new.jpg"],
            delete_image_ids=[img1.id],
        )
        updated = update_update(session, post.id, data)
        active = [img for img in updated.images if not img.is_deleted]
        assert len(active) == 1
        assert active[0].file_url == "/img/new.jpg"
        assert active[0].order_index == 0
        assert any(img.id == img1.id and img.is_deleted for img in updated.images)

    def test_does_not_delete_images_belonging_to_other_posts(self, setup_db):
        session = setup_db
        p1 = UpdatePost(title="P1", content="C", author="A")
        p2 = UpdatePost(title="P2", content="C", author="A")
        session.add_all([p1, p2])
        session.flush()
        img1 = UpdateImage(update_id=p1.id, file_url="/img/p1.jpg", order_index=0)
        img2 = UpdateImage(update_id=p2.id, file_url="/img/p2.jpg", order_index=0)
        session.add_all([img1, img2])
        session.commit()
        session.refresh(p1)

        data = UpdateEdit(
            title="P1", content="C", author="A",
            new_image_urls=[],
            delete_image_ids=[img2.id],
        )
        updated = update_update(session, p1.id, data)
        assert len(updated.images) == 1
        assert updated.images[0].file_url == "/img/p1.jpg"


class TestDeleteUpdate:
    def test_deletes_post_and_images(self, setup_db):
        session = setup_db
        post = UpdatePost(title="Delete Me", content="C", author="A")
        session.add(post)
        session.flush()
        session.add(UpdateImage(update_id=post.id, file_url="/img/1.jpg", order_index=0))
        session.commit()
        session.refresh(post)

        assert delete_update(session, post.id) is True
        assert get_update(session, post.id) is None

    def test_returns_false_for_missing_id(self, setup_db):
        assert delete_update(setup_db, 999) is False

    def test_does_not_affect_other_posts(self, setup_db):
        session = setup_db
        p1 = UpdatePost(title="Keep", content="C", author="A")
        p2 = UpdatePost(title="Delete", content="C", author="A")
        session.add_all([p1, p2])
        session.commit()
        session.refresh(p1)
        session.refresh(p2)

        delete_update(session, p2.id)
        assert get_update(session, p1.id) is not None


class TestBuildContentBlocks:
    def _make_post(self, content, image_urls=None):
        """Helper to build a post-like object with images for testing."""
        post = UpdatePost(title="T", content=content, author="A")
        post.id = 1
        if image_urls:
            post.images = [
                UpdateImage(update_id=1, file_url=url, order_index=i)
                for i, url in enumerate(image_urls)
            ]
        else:
            post.images = []
        return post

    def test_no_images_returns_all_text(self):
        post = self._make_post("line1\nline2\nline3")
        hero_intro, blocks = build_content_blocks(post)
        assert hero_intro == "line1"
        assert all(b["type"] == "text" for b in blocks)
        assert len(blocks) == 2
        assert blocks[0]["content"] == "line2"

    def test_empty_content_returns_no_blocks(self):
        post = self._make_post("")
        hero_intro, blocks = build_content_blocks(post)
        assert hero_intro is None
        assert blocks == []

    def test_blank_lines_filtered(self):
        post = self._make_post("line1\n\n\nline2\n\n")
        hero_intro, blocks = build_content_blocks(post)
        assert hero_intro == "line1"
        assert len(blocks) == 1

    def test_one_hero_image_only_no_inline(self):
        post = self._make_post("p1\np2\np3", ["hero.jpg"])
        hero_intro, blocks = build_content_blocks(post)
        assert hero_intro == "p1"
        assert all(b["type"] == "text" for b in blocks)
        assert len(blocks) == 2

    def test_stagger_basic(self):
        post = self._make_post("p1\np2\np3\np4\np5", ["hero.jpg", "a.jpg", "b.jpg"])
        hero_intro, blocks = build_content_blocks(post)
        assert hero_intro == "p1"
        text_indices = [i for i, b in enumerate(blocks) if b["type"] == "text"]
        img_indices = [i for i, b in enumerate(blocks) if b["type"] == "image"]
        assert len(text_indices) == 4
        assert len(img_indices) == 2
        assert img_indices[0] < img_indices[1]

    def test_stagger_positions_even(self):
        post = self._make_post("p1\np2\np3\np4\np5\np6\np7\np8",
                               ["hero.jpg", "a.jpg", "b.jpg", "c.jpg"])
        hero_intro, blocks = build_content_blocks(post)
        assert hero_intro == "p1"
        types = [b["type"] for b in blocks]
        assert types == ["text","text","image","text","text","image","text","text","image","text"]

    def test_more_images_than_paragraphs(self):
        post = self._make_post("p1\np2", ["hero.jpg", "a.jpg", "b.jpg", "c.jpg"])
        hero_intro, blocks = build_content_blocks(post)
        assert hero_intro == "p1"
        text_indices = [i for i, b in enumerate(blocks) if b["type"] == "text"]
        img_indices = [i for i, b in enumerate(blocks) if b["type"] == "image"]
        assert len(text_indices) == 1
        assert len(img_indices) == 3

    def test_single_paragraph_with_images(self):
        post = self._make_post("only one", ["hero.jpg", "a.jpg"])
        hero_intro, blocks = build_content_blocks(post)
        assert hero_intro == "only one"
        assert len(blocks) == 1
        assert blocks[0]["type"] == "image"

    def test_short_first_paragraph_fits_in_hero(self):
        short = " ".join(["word"] * 20)
        post = self._make_post(f"{short}\nsecond\nthird")
        hero_intro, blocks = build_content_blocks(post)
        assert hero_intro == short
        assert len(blocks) == 2
        assert blocks[0]["content"] == "second"
        assert blocks[1]["content"] == "third"

    def test_long_first_paragraph_truncated_for_hero(self):
        words = ["word"] * 80
        first_para = " ".join(words)
        post = self._make_post(f"{first_para}\nsecond\nthird", ["hero.jpg"])
        hero_intro, blocks = build_content_blocks(post)
        assert hero_intro.endswith("...")
        assert hero_intro.startswith("word word word")
        assert len(hero_intro.split()) == 60
        first_block = blocks[0]
        assert first_block["type"] == "text"
        assert first_block["content"] == " ".join(words[60:])
        assert len(blocks) == 3

    def test_very_long_first_paragraph_many_words(self):
        words = ["x"] * 120
        first_para = " ".join(words)
        post = self._make_post(f"{first_para}\nnext")
        hero_intro, blocks = build_content_blocks(post)
        assert hero_intro.endswith("...")
        assert len(hero_intro.split()) == 60
        assert blocks[0]["content"] == " ".join(words[60:])
        assert blocks[0]["type"] == "text"

    def test_long_first_paragraph_no_images(self):
        words = ["a"] * 70
        first_para = " ".join(words)
        post = self._make_post(f"{first_para}\nnext")
        hero_intro, blocks = build_content_blocks(post)
        assert hero_intro.endswith("...")
        assert blocks[0]["content"] == " ".join(words[60:])
        assert blocks[1]["content"] == "next"
