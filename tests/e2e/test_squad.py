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


class TestSquadPageE2E:
    def test_page_title(self, page):
        page.goto(f"{BASE_URL}/squad")
        assert "The Squad" in page.title()

    def test_heading_visible(self, page):
        page.goto(f"{BASE_URL}/squad")
        heading = page.locator("h1")
        assert heading.is_visible()
        assert heading.text_content() == "The Squad"

    def test_subtitle_visible(self, page):
        page.goto(f"{BASE_URL}/squad")
        subtitle = page.locator("text=10 people who made university unforgettable")
        assert subtitle.is_visible()

    def test_ten_member_cards_exist(self, page):
        page.goto(f"{BASE_URL}/squad")
        cards = page.locator("main a.group")
        assert cards.count() == 10

    def test_first_member_card_links_to_detail(self, page):
        page.goto(f"{BASE_URL}/squad")
        first_card = page.locator("main a.group").first
        first_card.click()
        page.wait_for_url("**/squad/1")
        assert "Alex Chen" in page.text_content("h1")

    def test_click_individual_member_from_name(self, page):
        page.goto(f"{BASE_URL}/squad")
        link = page.locator('a:has-text("Alex Chen")')
        link.click()
        page.wait_for_url("**/squad/1")

    def test_member_detail_shows_placeholder(self, page):
        page.goto(f"{BASE_URL}/squad/1")
        placeholder = page.locator("text=coming soon")
        assert placeholder.is_visible()

    def test_member_detail_back_link(self, page):
        page.goto(f"{BASE_URL}/squad/1")
        back = page.locator('a:has-text("Back to The Squad")')
        assert back.is_visible()
        back.click()
        page.wait_for_url("**/squad")
        assert page.url.rstrip("/").endswith("/squad")

    def test_invalid_member_returns_not_found(self, page):
        page.goto(f"{BASE_URL}/squad/99")
        assert page.locator("text=Member not found").is_visible()

    def test_navbar_has_squad_link_active(self, page):
        page.goto(f"{BASE_URL}/squad")
        nav_squad = page.locator('nav a:has-text("The Squad")')
        assert nav_squad.is_visible()

    def test_mobile_viewport_cards_stack(self, page):
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{BASE_URL}/squad")
        cards = page.locator("main a.group")
        first = cards.nth(0).bounding_box()
        second = cards.nth(1).bounding_box()
        assert second["y"] > first["y"] + first["height"] - 10

    def test_desktop_viewport_multiple_columns(self, page):
        page.set_viewport_size({"width": 1280, "height": 800})
        page.goto(f"{BASE_URL}/squad")
        cards = page.locator("main a.group")
        first = cards.nth(0).bounding_box()
        second = cards.nth(1).bounding_box()
        assert abs(second["y"] - first["y"]) < 20

    def test_no_console_errors(self, page):
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.goto(f"{BASE_URL}/squad")
        assert len(errors) == 0, f"Console errors: {errors}"
