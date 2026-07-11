import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, select

from app.main import app
from app.auth import hash_password
from app.database import engine
from app.models import Member
from app.seed import seed_members


TEST_PASSWORD = "testpass123"


@pytest.fixture(autouse=True)
def setup_app_db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_members(session)
        member = session.exec(select(Member).where(Member.username == "alex.chen")).first()
        member.hashed_password = hash_password(TEST_PASSWORD)
        session.add(member)
        session.commit()
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _login(client: TestClient):
    resp = client.post(
        "/login",
        data={"username": "alex.chen", "password": TEST_PASSWORD},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)


class TestNavbarAnonymous:
    def test_anonymous_shows_login(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert 'href="/login"' in resp.text
        assert ">Login<" in resp.text

    def test_anonymous_does_not_show_behind_curtain(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Behind the Curtain" not in resp.text

    def test_anonymous_does_not_show_logout(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert ">Logout<" not in resp.text


class TestNavbarLoggedIn:
    def test_logged_in_shows_logout(self, client, setup_app_db):
        _login(client)
        resp = client.get("/")
        assert resp.status_code == 200
        assert 'href="/logout"' in resp.text
        assert ">Logout<" in resp.text

    def test_logged_in_shows_behind_curtain(self, client, setup_app_db):
        _login(client)
        resp = client.get("/")
        assert resp.status_code == 200
        assert 'href="/behind-the-curtain"' in resp.text
        assert "Behind the Curtain" in resp.text

    def test_logged_in_hides_login_link(self, client, setup_app_db):
        _login(client)
        resp = client.get("/")
        assert resp.status_code == 200
        assert 'href="/login"' not in resp.text


class TestBehindTheCurtain:
    def test_redirect_when_anonymous(self, client):
        resp = client.get("/behind-the-curtain", follow_redirects=False)
        assert resp.status_code in (302, 303)
        assert resp.headers["location"] == "/login"

    def test_200_when_logged_in(self, client, setup_app_db):
        _login(client)
        resp = client.get("/behind-the-curtain")
        assert resp.status_code == 200
        assert "Behind the Curtain" in resp.text

    def test_contains_uploads_link(self, client, setup_app_db):
        _login(client)
        resp = client.get("/behind-the-curtain")
        assert 'href="/uploads"' in resp.text

    def test_contains_notes_link(self, client, setup_app_db):
        _login(client)
        resp = client.get("/behind-the-curtain")
        assert 'href="/notes"' in resp.text

    def test_contains_create_update_link(self, client, setup_app_db):
        _login(client)
        resp = client.get("/behind-the-curtain")
        assert 'href="/updates/new"' in resp.text

    def test_shows_member_name(self, client, setup_app_db):
        _login(client)
        resp = client.get("/behind-the-curtain")
        assert "Alex Chen" in resp.text
