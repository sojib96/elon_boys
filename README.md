# University Friends Group Website

A memory-preservation website for a 10-member university friends group. Built with FastAPI, deployed on Render with Supabase Postgres.

## Tech Stack

- **Backend:** FastAPI (Python)
- **Templating:** Jinja2 + Tailwind CSS (CDN)
- **Database:** Supabase Postgres + SQLModel
- **Storage:** Supabase Storage
- **Auth:** Session cookies + passlib (bcrypt)
- **Testing:** pytest + Playwright (Python)

## Local Development

```bash
# Clone the repository
git clone <repo-url>
cd elon_boys

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Copy env file and fill in your values
cp .env.example .env

# Run the development server
uvicorn app.main:app --reload --port 8001
```

Visit **http://127.0.0.1:8001** in your browser.

## Deploy to Render + Supabase

### Step 1: Create a Supabase project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click **New project**
3. Enter a name (e.g. `elon-boys-db`)
4. Set a strong database password and save it somewhere safe
5. Choose a region close to you (e.g. **US East (N. Virginia)**)
6. Click **Create new project** and wait ~2 minutes for provisioning

### Step 2: Get your Supabase credentials

Once the project is ready, go to **Project Settings** (the gear icon):

**Database connection string:**
1. Click **Database** in the left sidebar
2. Scroll to **Connection string**
3. Select **URI** mode
4. Copy the string — it looks like:
   `postgresql://postgres:<PASSWORD>@aws-0-<REGION>.pooler.supabase.com:6543/postgres`
5. Replace `<PASSWORD>` with the password you set in Step 1

**API keys:**
1. Click **API** in the left sidebar (under Project Settings or in the main nav)
2. Copy the **Project URL** (looks like `https://<id>.supabase.co`)
3. Copy the **service_role key** (NOT the anon public key — use service_role for backend access)

### Step 3: Run the schema on your Supabase database

Connect to your Supabase Postgres instance and create the tables. You can do this through the Supabase SQL Editor:

1. In your Supabase dashboard, go to **SQL Editor**
2. Click **New query**
3. Paste the following SQL and click **Run**:

```sql
-- Members table
CREATE TABLE IF NOT EXISTS member (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    nickname TEXT NOT NULL,
    photo_url TEXT,
    bio TEXT,
    fun_fact TEXT,
    current_status TEXT,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL
);

-- Timeline events table
CREATE TABLE IF NOT EXISTS timelineevent (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    photo_urls TEXT
);

-- Gallery items table
CREATE TABLE IF NOT EXISTS galleryitem (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL,
    file_url TEXT NOT NULL,
    uploaded_by TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- Update posts table
CREATE TABLE IF NOT EXISTS updatepost (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author TEXT NOT NULL,
    posted_at TIMESTAMP DEFAULT NOW()
);

-- Events table
CREATE TABLE IF NOT EXISTS event (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT,
    is_upcoming BOOLEAN DEFAULT TRUE
);

-- Guestbook entries table
CREATE TABLE IF NOT EXISTS guestbookentry (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    message TEXT NOT NULL,
    posted_at TIMESTAMP DEFAULT NOW()
);

-- Private uploads table
CREATE TABLE IF NOT EXISTS privateupload (
    id SERIAL PRIMARY KEY,
    file_url TEXT NOT NULL,
    uploaded_by TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- Internal notes table
CREATE TABLE IF NOT EXISTS internalnote (
    id SERIAL PRIMARY KEY,
    author TEXT NOT NULL,
    message TEXT NOT NULL,
    posted_at TIMESTAMP DEFAULT NOW()
);
```

### Step 4: Deploy to Render

1. Go to [render.com](https://render.com) and sign in with GitHub
2. Click **New +** → **Web Service**
3. Connect your GitHub repository (`sojib96/elon_boys`)
4. Configure the service:
   - **Name:** `elon-boys`
   - **Region:** Choose one close to your users (e.g. **Frankfurt** or **Virginia**)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
5. Click **Advanced** and add these environment variables:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Your Supabase Postgres URI (from Step 2) |
| `SUPABASE_URL` | Your Supabase project URL (from Step 2) |
| `SUPABASE_KEY` | Your Supabase service_role key (from Step 2) |
| `SECRET_KEY` | Generate one: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

6. Click **Create Web Service**
7. Wait ~3-5 minutes for the initial build and deploy

### Step 5: Verify deployment

Once the deploy is complete:
1. Click the URL Render gives you (e.g. `https://elon-boys.onrender.com`)
2. Visit `/` — you should see the homepage
3. Visit `/squad` — member list should load
4. Visit `/nonexistent-page` — you should see the custom 404 page

### Updating after changes

Render auto-deploys when you push to the `main` branch:

```bash
git add .
git commit -m "your changes"
git push origin main
```

Render will automatically rebuild and deploy your web service.

## Supabase Storage (for file uploads)

When you implement file uploads, files should be stored in Supabase Storage instead of the local filesystem. Here's how to set up:

1. In Supabase dashboard, go to **Storage**
2. Click **New bucket**
3. Name: `uploads`
4. Make it **public** (or configure RLS policies)
5. Use the Supabase Python client in your upload routes:

```python
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Upload a file
with open("path/to/file.jpg", "rb") as f:
    supabase.storage.from_("uploads").upload(
        "remote/path/file.jpg", f
    )

# Get public URL
public_url = supabase.storage.from_("uploads").get_public_url("remote/path/file.jpg")
```

## Project Structure

```
├── app/
│   ├── main.py             # FastAPI app, exception handlers
│   ├── database.py          # DB engine (Supabase Postgres / local SQLite fallback)
│   ├── models.py            # SQLModel table definitions
│   ├── auth.py              # Password hashing helpers
│   ├── jinja.py             # Jinja2 template config
│   ├── routers/
│   │   ├── public.py        # Public page routes (home, squad, gallery, etc.)
│   │   ├── private.py       # Private area routes (login, uploads, notes)
│   │   └── guestbook.py     # Guestbook route
│   ├── static/
│   │   └── uploads/         # Local uploads (gitignored)
│   └── templates/           # Jinja2 HTML templates
├── tests/                   # pytest + Playwright E2E tests
├── .env.example             # Required environment variables template
├── render.yaml              # Render Blueprint config
└── requirements.txt
```
