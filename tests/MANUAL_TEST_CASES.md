# Manual Test Cases — Homepage

## Prerequisites

- Server running at `http://127.0.0.1:8000`
- Tested in Chrome / Firefox / Edge

---

## Happy Path / Content

| # | Test | Expected | Pass/Fail |
|---|---|---|---|
| T1 | Navigate to `/` | Page loads with HTTP 200, no console errors | |
| T2 | Hero section visible above the fold | Tagline reads "Ten friends. Four years. A lifetime of memories." | |
| T3 | CTA button labeled "Meet the Squad" | Clicking navigates to `/squad` | |
| T4 | Tagline strip below hero | Text reads "We didn't realise we were making memories — we were just having fun." in italic on warm amber background | |
| T5 | 4 highlight cards present | Titles: "Our Story", "The Squad", "Timeline", "Gallery" | |
| T6 | Each card links to the correct page | Our Story → `/our-story`, Squad → `/squad`, Timeline → `/timeline`, Gallery → `/gallery` | |
| T7 | Closing quote strip before footer | Text reads "Here's to the nights we'll never forget…" in italic on warm amber background | |
| T8 | Navbar has all links | Our Story, The Squad, Timeline, Gallery, Updates, Events, Guestbook, Contact, Login | |
| T9 | Footer present | Copyright line "© 2026 Friends Group — Built with memories." | |

## Visual / Styling

| # | Test | Expected | Pass/Fail |
|---|---|---|---|
| V1 | CTA button background | Deep terracotta (`#b85c3e`) | |
| V2 | CTA button hover | Darkens to `#9e4d33` | |
| V3 | Card hover effects | Card lifts slightly (`-translate-y-1`) and shadow deepens (`shadow-xl`) | |
| V4 | Card title hover | Title turns terracotta (`#b85c3e`) on hover | |
| V5 | Page background | Warm off-white (`#faf7f2`) | |
| V6 | Hero overlay | Dark semi-transparent overlay over gradient for text readability | |
| V7 | Card icons visible | Book 📖, People 👥, Calendar 📅, Camera 📷 icons on respective cards | |
| V8 | Card subtitles visible | "How it all began", "Meet the 10 of us", "Year by year journey", "Photos & videos" | |

## Mobile / Responsive (use DevTools device toolbar)

| # | Test | Expected | Pass/Fail |
|---|---|---|---|
| M1 | Hero tagline wraps | "Ten friends. Four years." on one line, "A lifetime of memories." below it | |
| M2 | Cards stack single column | On screens < 640px, all 4 cards stack vertically full-width | |
| M3 | Cards go 2-column on tablet | On screens ≥ 640px, cards arrange 2×2 | |
| M4 | Cards go 4-column on desktop | On screens ≥ 1024px, cards arrange in one row of 4 | |
| M5 | Navbar links wrap | On narrow screens, nav links wrap to multiple lines (no horizontal overflow) | |
| M6 | Touch targets ≥ 44px | All buttons and links are reasonably tappable on mobile | |
| M7 | No horizontal scroll | Page content fits within viewport width at all breakpoints | |

## Navigation / Integration

| # | Test | Expected | Pass/Fail |
|---|---|---|---|
| N1 | `/our-story` loads | Returns 200, placeholder page renders | |
| N2 | `/squad` loads | Returns 200, placeholder page renders | |
| N3 | `/timeline` loads | Returns 200, placeholder page renders | |
| N4 | `/gallery` loads | Returns 200, placeholder page renders | |
| N5 | `/updates` loads | Returns 200, placeholder page renders | |
| N6 | `/events` loads | Returns 200, placeholder page renders | |
| N7 | `/guestbook` loads | Returns 200, placeholder page renders | |
| N8 | `/contact` loads | Returns 200, placeholder page renders | |
| N9 | `/login` loads | Returns 200, login page renders | |

## Edge Cases

| # | Test | Expected | Pass/Fail |
|---|---|---|---|
| E1 | Refresh the homepage multiple times | Consistent rendering, no flicker or layout shifts | |
| E2 | Disable JavaScript in browser | Page still renders (Tailwind CDN won't apply, but HTML content is visible) | |
| E3 | Resize browser window from narrow to wide | Cards reflow smoothly (responsive grid), no layout breakage | |
| E4 | Use browser Back after clicking a card | Returns to homepage, scroll position may reset (acceptable) | |
