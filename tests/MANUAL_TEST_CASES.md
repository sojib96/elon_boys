# Manual Test Cases

## Prerequisites

- Server running at `http://127.0.0.1:8001`
- Tested in Chrome / Firefox / Edge

---

## Homepage (Sprint 1)

### Happy Path / Content

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

### Visual / Styling

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

---

## Squad Page (Sprint 2)

### Content

| # | Test | Expected | Pass/Fail |
|---|---|---|---|
| S1 | Navigate to `/squad` | Page loads with HTTP 200, no console errors | |
| S2 | Page title | Browser tab reads "The Squad — Friends Group" | |
| S3 | Page heading | H1 reads "The Squad" in terracotta | |
| S4 | Subtitle visible | "The 10 people who made university unforgettable." | |
| S5 | All 10 members present | Alex Chen, Maya Rodriguez, James Okafor, Priya Sharma, Leo Kim, Sara Johansson, David Park, Aisha Mohammed, Tomás Silva, Yuki Tanaka | |
| S6 | Each card shows name + photo circle + bio + fun fact + status | Verify any 2–3 cards in full | |
| S7 | Initial circle on each card | Each card has a `rounded-full` gradient circle with 2-letter initials | |
| S8 | Fun fact badge on each card | Each card has an amber "Fun fact: …" pill | |
| S9 | Status line on each card | Each card has a "— Software Engineer at …" style line | |
| S10 | Card hover effect | Card lifts slightly on hover | |
| S11 | Card click navigates to detail page | Clicking any member card goes to `/squad/{id}` | |

### Member Detail Pages

| # | Test | Expected | Pass/Fail |
|---|---|---|---|
| D1 | Navigate to `/squad/1` | Shows Alex Chen's name, photo circle, bio, fun fact, status | |
| D2 | Placeholder text | Detail page shows "Full member profile — coming soon." | |
| D3 | Back link | "← Back to The Squad" link returns to `/squad` | |
| D4 | Invalid member ID (`/squad/99`) | Shows "Member not found" with back link | |

### Responsive

| # | Test | Expected | Pass/Fail |
|---|---|---|---|
| R1 | Mobile single column | At 375px width, cards stack vertically | |
| R2 | Desktop 3–4 columns | At 1280px width, cards arrange in multiple columns | |
| R3 | No horizontal scroll | Page fits viewport at all breakpoints | |

---

## Global Navigation (All Routes)

| # | Test | Expected | Pass/Fail |
|---|---|---|---|
| N1 | `/` loads | 200, homepage renders | |
| N2 | `/our-story` loads | 200, placeholder page renders | |
| N3 | `/squad` loads | 200, squad page renders | |
| N4 | `/timeline` loads | 200, placeholder page renders | |
| N5 | `/gallery` loads | 200, placeholder page renders | |
| N6 | `/updates` loads | 200, placeholder page renders | |
| N7 | `/events` loads | 200, placeholder page renders | |
| N8 | `/guestbook` loads | 200, placeholder page renders | |
| N9 | `/contact` loads | 200, placeholder page renders | |
| N10 | `/login` loads | 200, login page renders | |

## Timeline Page (Sprint 3)

### Content

| # | Test | Expected | Pass/Fail |
|---|---|---|---|
| T1 | Navigate to `/timeline` | Page loads with HTTP 200, no console errors | |
| T2 | Page title | Browser tab reads "Memory Timeline — Friends Group" | |
| T3 | Page heading | H1 reads "Memory Timeline" in terracotta | |
| T4 | Subtitle visible | "Our four-year journey, captured year by year." | |
| T5 | Four year sections | Year 1, Year 2, Year 3, Year 4 headings present | |
| T6 | Year detail labels | "Year 1 — The Beginning", "Year 4 — The Final Chapter", etc. | |
| T7 | Year badges | Four numbered circles (1–4) with terracotta background | |
| T8 | All 12 events present | Titles: First Day, Dorm Floor, Freshers, Road Trip, Study Sessions, Festival, House Share, Birthday, Internships, Final Year Project, Graduation Day, Farewell Dinner | |
| T9 | Event descriptions visible | Each card has a 1–2 line description | |
| T10 | Photo placeholders | Each card has a "Photo" banner area | |
| T11 | Terracotta + amber styling | Badges use terracotta, lines use amber | |

### Visual / Layout

| # | Test | Expected | Pass/Fail |
|---|---|---|---|
| V1 | Desktop: center line visible | Vertical amber line runs through the middle at ≥768px | |
| V2 | Desktop: alternating cards | Odd events on left, even events on right | |
| V3 | Desktop: connecting dots | Terracotta dots on the center line between card rows | |
| V4 | Mobile: single column | At 375px, cards stack full-width, no center line | |
| V5 | Card hover effect | Cards have subtle shadow increase on hover | |

### Navigation

| # | Test | Expected | Pass/Fail |
|---|---|---|---|
| N1 | Navbar "Timeline" link visible | Clickable link in the top nav | |
| N2 | All other routes still work | `/`, `/squad`, `/gallery`, etc. return 200 | |

## Edge Cases

| # | Test | Expected | Pass/Fail |
|---|---|---|---|
| E1 | Refresh any page repeatedly | Consistent rendering, no flicker | |
| E2 | Disable JavaScript | HTML content still renders (Tailwind styles lost, layout degrades gracefully) | |
| E3 | Resize from narrow to wide | Grids reflow smoothly, no breakage | |
| E4 | Browser Back after clicking a card/link | Returns to previous page (scroll may reset) | |
