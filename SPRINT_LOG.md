# Sprint Log

## Sprint 1 — Homepage

**Role:** UI/UX Designer → Full-Stack Developer → QA

### Goal

Design and implement the public homepage hero, tagline strip, 4 memory highlight cards, and closing quote — per the approved design spec.

### Delivered

- **Homepage template** (`app/templates/home.html`): hero with gradient + dark overlay + tagline + terracotta CTA button ("Meet the Squad"), amber tagline strip, 4-card grid (Our Story / The Squad / Timeline / Gallery), closing nostalgic quote
- **base.html** update: added `{% block hero %}` for full-width sections, changed body background to warm off-white `#faf7f2`, text to `stone-800`, footer to `stone-400`
- **Color palette**: terracotta `#b85c3e` primary, amber `#f59e0b` accent, warm off-white base
- **13 API tests** (`tests/test_public_routes.py`): route availability, content checks, color presence — all passing
- **12 E2E tests** (`tests/e2e/test_homepage.py`): Playwright browser tests for navigation, responsive layout, hover effects, console errors

### Known Issues / Left for Later

- Navbar still uses indigo-600 (brand colors only on homepage content; navbar polish deferred)
- No real images — all placeholders (gradients + unicode icons)
- E2E tests require the dev server to be running on port 8001 (or set `TEST_URL` env var)
- Playwright `chromium` browser must be installed (`python -m playwright install chromium`)
