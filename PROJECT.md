# PROJECT.md — University Friends Group Website

> This file is the single source of truth for this project. Keep it in the
> project's root directory so any AI coding tool can read it for context
> before doing any work.

---

## 1. Project Overview

**Name:** [Your Group Name] Website
**Type:** Personal memory-preservation website for a 10-member university
friends group, with a public area and a private login-protected area.

**One-liner:** A website to preserve our university memories (photos,
stories, timeline) and share ongoing updates — public for anyone to browse,
private area for the 10 of us to freely upload and chat.

---

## 2. Motivation

We are a group of 10 friends from university who want a permanent home for
our shared memories — separate from social media, which is noisy and
temporary. Purpose:
1. **Preserve** — photos, stories, and moments from our university years in
   one organized place that won't get lost or buried.
2. **Share** — let friends, and anyone we choose, see our story and current
   updates (reunions, achievements, life updates).
3. **Stay connected** — a private space for just the 10 of us to keep
   uploading and chatting long after graduation.

---

## 3. Users

- **Public visitors** — no login, can browse everything except the private
  area.
- **10 fixed members** — have login access to the private area (upload
  raw photos/videos, post internal notes).
- No public sign-up. No admin panel needed beyond the 10 fixed accounts
  (can be added manually).

---

## 4. Feature List / Site Map

### Public Area (no login required)
| Page | Purpose |
|---|---|
| Home | Banner, tagline, highlight links |
| Our Story | How the group formed |
| The Squad | 10 member profile cards |
| Memory Timeline | Year-by-year journey (Year 1–4) |
| Gallery | Photos/videos organized by event/category |
| Updates | Blog-style posts — news, life updates |
| Events | Past/upcoming reunions and meetups |
| Guestbook | Anyone can leave a short public message |
| Contact | Contact info / social links |

### Private Area (login required — 10 members only)
| Page | Purpose |
|---|---|
| Member Login | Simple login form, 10 fixed accounts |
| Private Uploads | Raw/unfiltered photo & video dump |
| Internal Notes | Simple message board for the group |

---

## 5. Tech Stack (Python-based, modern, free, maintainable solo)

| Layer | Choice | Why |
|---|---|---|
| Backend framework | **FastAPI** | Modern, fast, async, great docs, Python-native |
| Templating / Frontend | **Jinja2 + HTMX + Tailwind CSS** | Stay 100% Python — HTMX adds interactivity without needing React/Node; Tailwind for clean styling |
| Database | **SQLite + SQLModel** | Zero-cost, file-based, perfect for ~10 users; SQLModel (by FastAPI's creator) gives clean Python models |
| Auth | **Session cookies + passlib (password hashing)** | Simple, secure enough for 10 fixed accounts, no need for a heavy auth service |
| File storage | **Local `/static/uploads` folder** | Free, simple; can move to cloud storage later if it grows |
| Testing | **pytest (unit/API) + Playwright for Python (E2E)** | Modern Python-native testing stack |
| Hosting | **Render.com or Railway (free tier)** | Deploys Python apps directly from GitHub, free tier is enough for low traffic |
| Version control | **GitHub** | Standard, connects directly to hosting for auto-deploy |

**Not using:** React/Next.js/Node — intentionally skipped since you're
maintaining this yourself and want a pure Python stack.

---

## 6. Project Structure (target folder layout)

```
project-root/
├── PROJECT.md                 # this file
├── app/
│   ├── main.py                 # FastAPI app entrypoint
│   ├── models.py                # SQLModel database models
│   ├── database.py              # DB connection/session setup
│   ├── auth.py                   # login/session logic
│   ├── routers/
│   │   ├── public.py             # public page routes
│   │   ├── private.py            # login-protected routes
│   │   └── guestbook.py
│   ├── templates/                # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── squad.html
│   │   ├── timeline.html
│   │   ├── gallery.html
│   │   ├── updates.html
│   │   ├── events.html
│   │   ├── guestbook.html
│   │   ├── contact.html
│   │   └── private/
│   │       ├── login.html
│   │       ├── uploads.html
│   │       └── notes.html
│   └── static/
│       ├── css/
│       ├── js/
│       └── uploads/              # stored photos/videos
├── tests/
│   ├── test_public_routes.py
│   ├── test_auth.py
│   └── e2e/                       # Playwright tests
├── requirements.txt
├── .env.example                   # environment variable template
└── README.md
```

---

## 7. Data Model (initial draft)

- **Member** — id, name, nickname, photo_url, bio, fun_fact, current_status,
  username, hashed_password
- **TimelineEvent** — id, year, title, description, photo_urls
- **GalleryItem** — id, category, file_url, uploaded_by, uploaded_at
- **UpdatePost** — id, title, content, author, posted_at
- **Event** — id, title, date, description, is_upcoming
- **GuestbookEntry** — id, name, message, posted_at
- **PrivateUpload** — id, file_url, uploaded_by, uploaded_at
- **InternalNote** — id, author, message, posted_at

---

## 8. Non-Functional Requirements

- Must run entirely on free-tier services (no ongoing cost)
- Mobile-responsive (majority of visitors will use phones)
- Simple enough for one Python developer (you) to maintain long-term
- Private area must be genuinely inaccessible without login (server-side
  session check, not just hidden UI)

---

## 9. Development Approach

This project is being built using an AI coding tool, following an agile
sprint process where the AI rotates through roles (UI/UX Designer, Frontend
Developer, Backend Developer, QA/SQA) with human review between each stage.
See the companion file `AI-PROMPTS-GUIDE.md` for the exact step-by-step
process.

---

## 10. Deployment Plan

1. Push code to a GitHub repository
2. Connect repository to Render.com or Railway (free tier)
3. Set environment variables (secret key, DB path) in the hosting dashboard
4. Auto-deploy on every push to `main`
