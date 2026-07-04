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


class TestTimelinePageE2E:
    def test_page_title(self, page):
        page.goto(f"{BASE_URL}/timeline")
        assert "Memory Timeline" in page.title()

    def test_heading_visible(self, page):
        page.goto(f"{BASE_URL}/timeline")
        heading = page.locator("h1")
        assert heading.is_visible()
        assert "Memory Timeline" in heading.text_content()

    def test_subtitle_visible(self, page):
        page.goto(f"{BASE_URL}/timeline")
        assert page.locator("text=four-year journey").is_visible()

    def test_four_year_sections(self, page):
        page.goto(f"{BASE_URL}/timeline")
        for year in ["Year 1", "Year 2", "Year 3", "Year 4"]:
            assert page.locator(f"h2:has-text('{year}')").is_visible()

    def test_year_badges_visible(self, page):
        page.goto(f"{BASE_URL}/timeline")
        for i in range(1, 5):
            badge = page.locator(f"text={i}").first
            assert badge.is_visible()

    def test_event_cards_have_titles(self, page):
        page.goto(f"{BASE_URL}/timeline")
        for title in ["First Day of University", "Graduation Day", "Farewell Dinner"]:
            assert page.locator(f"h3:has-text('{title}')").is_visible()

    def test_event_cards_have_descriptions(self, page):
        page.goto(f"{BASE_URL}/timeline")
        assert page.locator("text=Ten strangers walked").is_visible()
        assert page.locator("text=Caps in the air").is_visible()

    def test_twelve_event_cards_exist(self, page):
        page.goto(f"{BASE_URL}/timeline")
        cards = page.locator("h3")
        assert cards.count() == 12

    def test_photo_placeholders(self, page):
        page.goto(f"{BASE_URL}/timeline")
        photo_labels = page.locator("span:has-text('Photo')")
        assert photo_labels.count() == 12

    def test_mobile_viewport(self, page):
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{BASE_URL}/timeline")
        assert page.locator("h1:has-text('Memory Timeline')").is_visible()
        assert page.locator("text=Year 1").is_visible()

    def test_navbar_timeline_link(self, page):
        page.goto(f"{BASE_URL}/timeline")
        nav_link = page.locator('#desktop-nav a:has-text("Timeline")')
        assert nav_link.is_visible()

    def test_no_console_errors(self, page):
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.goto(f"{BASE_URL}/timeline")
        assert len(errors) == 0, f"Console errors: {errors}"
