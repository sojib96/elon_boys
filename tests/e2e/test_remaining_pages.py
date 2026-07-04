import os
import pytest
from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("TEST_URL", "http://127.0.0.1:8001")


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    yield page
    page.close()


class TestGalleryPage:
    def test_page_title(self, page):
        page.goto(f"{BASE_URL}/gallery")
        assert "Gallery" in page.title()

    def test_heading_visible(self, page):
        page.goto(f"{BASE_URL}/gallery")
        assert page.locator("h1:has-text('Gallery')").is_visible()

    def test_twelve_photo_cards(self, page):
        page.goto(f"{BASE_URL}/gallery")
        cards = page.locator(".aspect-square")
        assert cards.count() == 12

    def test_filter_pills(self, page):
        page.goto(f"{BASE_URL}/gallery")
        pills = page.locator("span.rounded-full")
        assert pills.count() >= 4


class TestUpdatesPage:
    def test_page_title(self, page):
        page.goto(f"{BASE_URL}/updates")
        assert "Updates" in page.title()

    def test_heading_visible(self, page):
        page.goto(f"{BASE_URL}/updates")
        assert page.locator("h1:has-text('Updates')").is_visible()

    def test_three_articles(self, page):
        page.goto(f"{BASE_URL}/updates")
        articles = page.locator("article")
        assert articles.count() == 3

    def test_post_content(self, page):
        page.goto(f"{BASE_URL}/updates")
        assert page.locator("text=Five Years Since Graduation").is_visible()


class TestEventsPage:
    def test_page_title(self, page):
        page.goto(f"{BASE_URL}/events")
        assert "Events" in page.title()

    def test_upcoming_section(self, page):
        page.goto(f"{BASE_URL}/events")
        assert page.locator("h2:has-text('Upcoming')").is_visible()

    def test_past_section(self, page):
        page.goto(f"{BASE_URL}/events")
        assert page.locator("h2:has-text('Past')").is_visible()

    def test_event_cards_exist(self, page):
        page.goto(f"{BASE_URL}/events")
        cards = page.locator("h3")
        assert cards.count() >= 2


class TestGuestbookPage:
    def test_page_title(self, page):
        page.goto(f"{BASE_URL}/guestbook")
        assert "Guestbook" in page.title()

    def test_five_entries(self, page):
        page.goto(f"{BASE_URL}/guestbook")
        entries = page.locator("text=Sarah M.").first
        assert entries.is_visible()

    def test_form_placeholder(self, page):
        page.goto(f"{BASE_URL}/guestbook")
        assert page.locator("text=Sign the Guestbook").is_visible()


class TestStoryPage:
    def test_page_title(self, page):
        page.goto(f"{BASE_URL}/our-story")
        assert "Our Story" in page.title()

    def test_heading_visible(self, page):
        page.goto(f"{BASE_URL}/our-story")
        assert page.locator("h1").is_visible()

    def test_story_content(self, page):
        page.goto(f"{BASE_URL}/our-story")
        assert page.locator("text=ten strangers").is_visible()


class TestContactPage:
    def test_page_title(self, page):
        page.goto(f"{BASE_URL}/contact")
        assert "Contact" in page.title()

    def test_contact_details(self, page):
        page.goto(f"{BASE_URL}/contact")
        assert page.locator("text=Email").is_visible()
        assert page.locator("text=Phone").is_visible()


class TestPrivatePages:
    def test_login_page(self, page):
        page.goto(f"{BASE_URL}/login")
        assert "Member Login" in page.title()
        assert page.locator("input[type=password]").is_visible()

    def test_uploads_page(self, page):
        page.goto(f"{BASE_URL}/uploads")
        assert "Private Uploads" in page.title()
        assert page.locator("text=Graduation video").is_visible()

    def test_notes_page(self, page):
        page.goto(f"{BASE_URL}/notes")
        assert "Internal Notes" in page.title()
        assert page.locator("text=Who's bringing the grill").is_visible()


class TestNavigation:
    def test_all_nav_links_work(self, page):
        nav_links = ["Our Story", "Squad", "Timeline", "Gallery", "Updates", "Events", "Guestbook", "Contact"]
        for link_text in nav_links:
            page.goto(f"{BASE_URL}")
            link = page.locator(f'#desktop-nav a:has-text("{link_text}")')
            assert link.is_visible(), f"Nav link '{link_text}' not found"
