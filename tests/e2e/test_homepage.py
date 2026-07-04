import pytest
from playwright.sync_api import sync_playwright

import os
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


class TestHomepageE2E:
    def test_page_title(self, page):
        page.goto(BASE_URL)
        assert "Home" in page.title()

    def test_hero_visible(self, page):
        page.goto(BASE_URL)
        hero = page.locator("h1")
        assert hero.is_visible()
        assert "Ten friends" in hero.text_content()

    def test_cta_button_navigates_to_squad(self, page):
        page.goto(BASE_URL)
        cta = page.locator('a:has-text("Meet the Squad")')
        assert cta.is_visible()
        cta.click()
        page.wait_for_url("**/squad")
        assert page.url.endswith("/squad")

    def test_four_cards_visible(self, page):
        page.goto(BASE_URL)
        cards = page.locator("main a.group")
        assert cards.count() == 4

    def test_card_links_navigate(self, page):
        page.goto(BASE_URL)
        card = page.locator("main a.group").filter(has_text="Our Story")
        card.click()
        page.wait_for_url("**/our-story")
        assert page.url.endswith("/our-story")

    def test_squad_card_navigates(self, page):
        page.goto(BASE_URL)
        card = page.locator('a:has-text("The Squad")').first
        card.click()
        page.wait_for_url("**/squad")
        assert page.url.endswith("/squad")

    def test_tagline_strip_visible(self, page):
        page.goto(BASE_URL)
        strip = page.locator("section:has-text('just having fun')")
        assert strip.is_visible()

    def test_closing_quote_visible(self, page):
        page.goto(BASE_URL)
        quote = page.locator("section:has-text('never forget')")
        assert quote.is_visible()

    def test_navbar_has_login_link(self, page):
        page.goto(BASE_URL)
        login = page.locator('a:has-text("Login")')
        assert login.is_visible()

    def test_footer_visible(self, page):
        page.goto(BASE_URL)
        footer = page.locator("footer")
        assert footer.is_visible()
        assert "Built with memories" in footer.text_content()

    def test_mobile_viewport_cards_stack(self, page):
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(BASE_URL)
        cards = page.locator("main a.group")
        assert cards.count() == 4
        first_card = cards.nth(0)
        second_card = cards.nth(1)
        first_box = first_card.bounding_box()
        second_box = second_card.bounding_box()
        assert second_box["y"] > first_box["y"] + first_box["height"] - 10

    def test_desktop_viewport_cards_in_row(self, page):
        page.set_viewport_size({"width": 1280, "height": 800})
        page.goto(BASE_URL)
        cards = page.locator("main a.group")
        first_card = cards.nth(0)
        second_card = cards.nth(1)
        first_box = first_card.bounding_box()
        second_box = second_card.bounding_box()
        assert abs(second_box["y"] - first_box["y"]) < 20

    def test_cta_button_has_terracotta_color(self, page):
        page.goto(BASE_URL)
        cta = page.locator('a:has-text("Meet the Squad")')
        bg = cta.evaluate("el => getComputedStyle(el).backgroundColor")
        rgb = [int(x) for x in bg.strip("rgb()").split(",")]
        assert rgb[0] > 150 and rgb[1] < 100 and rgb[2] < 80

    def test_no_console_errors(self, page):
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.goto(BASE_URL)
        assert len(console_errors) == 0, f"Console errors: {console_errors}"
