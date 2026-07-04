# University Friends Group Website

A memory-preservation website for a 10-member university friends group.

## Tech Stack

- **Backend:** FastAPI (Python)
- **Templating:** Jinja2 + HTMX + Tailwind CSS (CDN)
- **Database:** SQLite + SQLModel
- **Auth:** Session cookies + passlib (bcrypt)
- **Testing:** pytest + Playwright (Python)

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd <project-folder>

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --reload
```

Visit **http://127.0.0.1:8000** in your browser.

## Project Structure

See `PROJECT.md` for the full project brief and folder layout.
