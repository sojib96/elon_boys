from fastapi.testclient import TestClient
import pytest

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


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
    "/uploads",
    "/notes",
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
        assert "#e85d3a" in resp.text

    def test_homepage_warm_background(self, client):
        resp = client.get("/")
        assert "surface" in resp.text

    def test_squad_page_loads(self, client):
        resp = client.get("/squad")
        assert resp.status_code == 200
        assert "The Squad" in resp.text

    def test_squad_all_members_present(self, client):
        resp = client.get("/squad")
        for name in ["Alex Chen", "Maya Rodriguez", "James Okafor", "Priya Sharma",
                      "Leo Kim", "Sara Johansson", "David Park", "Aisha Mohammed",
                      "Tomás Silva", "Yuki Tanaka"]:
            assert name in resp.text, f"Missing member: {name}"

    def test_squad_ten_initial_circles(self, client):
        resp = client.get("/squad")
        assert resp.text.count("rounded-full flex items-center") == 10

    def test_squad_fun_fact_badges(self, client):
        resp = client.get("/squad")
        assert resp.text.count("rounded-full") >= 20

    def test_squad_status_lines(self, client):
        resp = client.get("/squad")
        for status in ["Google", "NYU", "Kola", "NASA", "Figma",
                        "Writer", "Teacher", "Hospital", "Producer", "Tokyo"]:
            assert status in resp.text, f"Missing status: {status}"

    def test_squad_terracotta_heading(self, client):
        resp = client.get("/squad")
        assert '#e85d3a' in resp.text

    def test_squad_responsive_grid(self, client):
        resp = client.get("/squad")
        assert "lg:grid-cols-3" in resp.text
        assert "sm:grid-cols-2" in resp.text
        assert "xl:grid-cols-4" in resp.text

    def test_squad_card_hover_effect(self, client):
        resp = client.get("/squad")
        assert "hover:shadow-sm" in resp.text or "hover:-translate-y-1" in resp.text

    def test_squad_member_detail_valid(self, client):
        resp = client.get("/squad/1")
        assert resp.status_code == 200
        assert "Alex Chen" in resp.text
        assert "coming soon" in resp.text

    def test_squad_member_detail_invalid(self, client):
        resp = client.get("/squad/99")
        assert resp.status_code == 200
        assert "Member not found" in resp.text

    def test_squad_member_detail_back_link(self, client):
        resp = client.get("/squad/1")
        assert "Back to The Squad" in resp.text
        assert 'href="/squad"' in resp.text

    def test_timeline_page_loads(self, client):
        resp = client.get("/timeline")
        assert resp.status_code == 200
        assert "Memory Timeline" in resp.text

    def test_timeline_subtitle(self, client):
        resp = client.get("/timeline")
        assert "four-year journey" in resp.text

    def test_timeline_all_years_present(self, client):
        resp = client.get("/timeline")
        for year in ["Year 1", "Year 2", "Year 3", "Year 4"]:
            assert year in resp.text, f"Missing {year}"

    def test_timeline_all_events_present(self, client):
        resp = client.get("/timeline")
        for title in ["First Day of University", "Graduation Day", "Farewell Dinner",
                       "Spring Break Road Trip", "House Share Begins"]:
            assert title in resp.text, f"Missing event: {title}"

    def test_timeline_twelve_events(self, client):
        resp = client.get("/timeline")
        assert resp.text.count("card-sparkle") == 15

    def test_timeline_year_badges(self, client):
        resp = client.get("/timeline")
        for year_label in ["Year 1", "Year 2", "Year 3", "Year 4"]:
            assert year_label in resp.text, f"Missing {year_label}"

    def test_timeline_photo_placeholders(self, client):
        resp = client.get("/timeline")
        assert resp.text.count("Photo") >= 12

    def test_timeline_terracotta(self, client):
        resp = client.get("/timeline")
        assert "#e85d3a" in resp.text

    def test_gallery_page_loads(self, client):
        resp = client.get("/gallery")
        assert resp.status_code == 200
        assert "Gallery" in resp.text

    def test_gallery_has_items(self, client):
        resp = client.get("/gallery")
        assert resp.text.count("gallery-card") >= 18

    def test_gallery_categories(self, client):
        resp = client.get("/gallery")
        for cat in ["Events", "Trips", "Campus Life", "Random"]:
            assert cat in resp.text

    def test_updates_page_loads(self, client):
        resp = client.get("/updates")
        assert resp.status_code == 200
        assert "Updates" in resp.text

    def test_updates_three_posts(self, client):
        resp = client.get("/updates")
        assert resp.text.count("card-sparkle") == 6

    def test_events_page_loads(self, client):
        resp = client.get("/events")
        assert resp.status_code == 200
        assert "Events" in resp.text

    def test_events_upcoming_and_past(self, client):
        resp = client.get("/events")
        assert "Upcoming" in resp.text
        assert "Past" in resp.text

    def test_guestbook_page_loads(self, client):
        resp = client.get("/guestbook")
        assert resp.status_code == 200
        assert "Guestbook" in resp.text

    def test_guestbook_five_entries(self, client):
        resp = client.get("/guestbook")
        assert resp.text.count("card-sparkle") == 8

    def test_story_page_loads(self, client):
        resp = client.get("/our-story")
        assert resp.status_code == 200
        assert "Our Story" in resp.text

    def test_contact_page_loads(self, client):
        resp = client.get("/contact")
        assert resp.status_code == 200
        assert "Contact" in resp.text

    def test_login_page_loads(self, client):
        resp = client.get("/login")
        assert resp.status_code == 200
        assert "Member Login" in resp.text

    def test_uploads_page_loads(self, client):
        resp = client.get("/uploads")
        assert resp.status_code == 200
        assert "Private Uploads" in resp.text

    def test_notes_page_loads(self, client):
        resp = client.get("/notes")
        assert resp.status_code == 200
        assert "Internal Notes" in resp.text

    def test_404_page(self, client):
        resp = client.get("/nonexistent-page")
        assert resp.status_code == 404
        assert "Page Not Found" in resp.text
        assert "Go Home" in resp.text
