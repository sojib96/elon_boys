from fastapi.testclient import TestClient
import pytest

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


ROUTES_200 = [
    "/",
    "/our-story",
    "/squad",
    "/timeline",
    "/gallery",
    "/updates",
    "/events",
    "/guestbook",
    "/contact",
    "/login",
]


class TestPublicRoutes:
    def test_all_routes_return_200(self, client):
        for route in ROUTES_200:
            resp = client.get(route)
            assert resp.status_code == 200, f"{route} returned {resp.status_code}"

    def test_homepage_title(self, client):
        resp = client.get("/")
        assert "<title>Home" in resp.text

    def test_homepage_hero_tagline(self, client):
        resp = client.get("/")
        assert "Ten friends. Four years." in resp.text
        assert "A lifetime of memories." in resp.text

    def test_homepage_cta_button(self, client):
        resp = client.get("/")
        assert "Meet the Squad" in resp.text
        assert 'href="/squad"' in resp.text

    def test_homepage_tagline_strip(self, client):
        resp = client.get("/")
        assert "we were just having fun" in resp.text

    def test_homepage_has_four_cards(self, client):
        resp = client.get("/")
        for title in ["Our Story", "The Squad", "Timeline", "Gallery"]:
            assert title in resp.text, f"Missing card: {title}"

    def test_card_links(self, client):
        resp = client.get("/")
        for path in ["/our-story", "/squad", "/timeline", "/gallery"]:
            assert f'href="{path}"' in resp.text, f"Missing link: {path}"

    def test_closing_quote(self, client):
        resp = client.get("/")
        assert "never forget" in resp.text

    def test_navbar_links(self, client):
        resp = client.get("/")
        for label in [
            "Our Story", "The Squad", "Timeline", "Gallery",
            "Updates", "Events", "Guestbook", "Contact", "Login",
        ]:
            assert label in resp.text, f"Missing nav link: {label}"

    def test_footer(self, client):
        resp = client.get("/")
        assert "Built with memories" in resp.text

    def test_homepage_contains_terracotta(self, client):
        resp = client.get("/")
        assert "#b85c3e" in resp.text

    def test_homepage_warm_background(self, client):
        resp = client.get("/")
        assert "#faf7f2" in resp.text

    def test_squad_page_loads(self, client):
        resp = client.get("/squad")
        assert resp.status_code == 200
        assert "The Squad" in resp.text
