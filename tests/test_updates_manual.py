import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.auth import hash_password
from app.main import app
from app.models import Member, UpdateImage, UpdatePost
from app.database import engine
from app.services.updates import create_update, seed_if_empty
from app.schemas import UpdateCreate


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def authed_client():
    """Return a TestClient logged in as a test member."""
    with TestClient(app) as c:
        with Session(engine) as session:
            member = session.exec(select(Member).where(Member.username == "alex.chen")).first()
            if member is None:
                member = Member(
                    username="alex.chen",
                    full_name="Alex Chen",
                    tag="@alexchen",
                    email="alex@test.com",
                    hashed_password=hash_password("testpass123"),
                )
                session.add(member)
                session.commit()
            else:
                member.hashed_password = hash_password("testpass123")
                session.commit()

        resp = c.post("/login", data={"username": "alex.chen", "password": "testpass123"})
        assert resp.status_code in (200, 303)
        yield c


@pytest.fixture
def seeded_post():
    """Create a fresh post for tests that need a specific post."""
    with Session(engine) as session:
        post = UpdatePost(title="Test Post", content="Test content", author="Test Author")
        session.add(post)
        session.commit()
        session.refresh(post)
        post_id = post.id
    return post_id


class TestUpdatesIntegration:
    def test_list_page(self, client):
        resp = client.get("/updates")
        assert resp.status_code == 200
        assert "Updates" in resp.text

    def test_detail_page(self, seeded_post, client):
        resp = client.get(f"/updates/{seeded_post}")
        assert resp.status_code == 200
        assert "Test Post" in resp.text
        assert "Test Author" in resp.text

    def test_detail_uses_db_image(self, seeded_post, client):
        with Session(engine) as session:
            session.add(UpdateImage(update_id=seeded_post, file_url="/static/uploads/updates/test.jpg", order_index=0))
            session.commit()
        resp = client.get(f"/updates/{seeded_post}")
        assert "/static/uploads/updates/test.jpg" in resp.text

    def test_related_posts_section(self, seeded_post, client):
        resp = client.get(f"/updates/{seeded_post}")
        assert resp.status_code == 200

    def test_404_for_missing(self, client):
        resp = client.get("/updates/999")
        assert resp.status_code == 404

    def test_seed_idempotent(self, client):
        client.get("/updates")
        resp = client.get("/updates")
        assert resp.status_code == 200
        assert resp.text.count('href="/updates/') >= 8

    def test_detail_shows_edit_buttons_when_logged_in(self, seeded_post, authed_client):
        resp = authed_client.get(f"/updates/{seeded_post}")
        assert resp.status_code == 200
        assert f"/updates/{seeded_post}/edit" in resp.text

    def test_detail_hides_edit_buttons_when_logged_out(self, seeded_post, client):
        resp = client.get(f"/updates/{seeded_post}")
        assert resp.status_code == 200
        assert f"/updates/{seeded_post}/edit" not in resp.text


class TestEditUpdateIntegration:
    def test_edit_form_loads(self, seeded_post, authed_client):
        resp = authed_client.get(f"/updates/{seeded_post}/edit")
        assert resp.status_code == 200
        assert "Edit Update" in resp.text
        assert "Test Post" in resp.text

    def test_edit_form_pre_fills_fields(self, seeded_post, authed_client):
        resp = authed_client.get(f"/updates/{seeded_post}/edit")
        assert 'value="Test Post"' in resp.text
        assert 'Test content' in resp.text

    def test_edit_submit_updates_post(self, seeded_post, authed_client):
        resp = authed_client.post(
            f"/updates/{seeded_post}/edit",
            data={
                "title": "Updated Title",
                "content": "Updated content body",
                "excerpt": "Updated excerpt",
                "author": "Alex Chen",
            },
        )
        assert resp.status_code == 200
        assert "Updated Title" in resp.text
        assert "Updated content body" in resp.text

    def test_edit_submit_validation_errors(self, seeded_post, authed_client):
        resp = authed_client.post(
            f"/updates/{seeded_post}/edit",
            data={"title": "", "content": "", "author": ""},
        )
        assert resp.status_code == 422
        assert "Title is required." in resp.text
        assert "Content is required." in resp.text
        assert "Author is required." in resp.text

    def test_edit_404_for_missing(self, authed_client):
        resp = authed_client.get("/updates/999/edit")
        assert resp.status_code == 404


class TestDeleteUpdateIntegration:
    def test_delete_removes_post(self, authed_client):
        with Session(engine) as session:
            post = UpdatePost(title="Delete Me", content="Body", author="A")
            session.add(post)
            session.commit()
            session.refresh(post)
            post_id = post.id

        resp = authed_client.post(f"/updates/{post_id}/delete")
        assert resp.status_code == 200
        resp = authed_client.get(f"/updates/{post_id}")
        assert resp.status_code == 404

    def test_delete_redirects_to_list(self, authed_client):
        with Session(engine) as session:
            post = UpdatePost(title="Redirect Test", content="Body", author="A")
            session.add(post)
            session.commit()
            session.refresh(post)
            post_id = post.id

        resp = authed_client.post(f"/updates/{post_id}/delete", follow_redirects=False)
        assert resp.status_code in (302, 303)
        assert resp.headers["location"] == "/updates"

    def test_delete_404_for_missing(self, authed_client):
        resp = authed_client.post("/updates/999/delete")
        assert resp.status_code == 404
