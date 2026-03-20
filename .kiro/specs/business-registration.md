# Spec: Business Registration

## Goal
Allow minority-owned business owners to self-register with their story,
category, location, contact info, and optional AI-generated founder story.

## User Stories
- As a business owner, I can register my business with name, description, story, category, address, phone, and website
- As a business owner, I can click "Write with AI" to generate a founder story from my basic inputs
- As a visitor, I can browse all approved businesses on the homepage
- As a visitor, I can filter businesses by category using pill buttons
- As a visitor, I can search businesses by name or description
- As a visitor, I can click a business card to see its full profile

## Acceptance Criteria
- [x] Registration form validates all required fields before submission
- [x] Business saved to SQLite with `is_approved = 1` (auto-approved for hackathon)
- [x] Confirmation toast shown after successful registration
- [x] User redirected to new business profile page after 2 seconds
- [x] AI story writer calls `POST /api/agents/generate-story` with form data
- [x] Generated story populates the textarea and can be edited before submit
- [x] Business appears in homepage grid immediately after registration
- [x] Category filter pills filter the grid in real time

## API Endpoints
- `GET  /api/businesses` — list all approved businesses (supports `?category=` and `?search=`)
- `GET  /api/businesses/{id}` — single business with nested deals and reviews
- `POST /api/businesses` — register new business

## Data Model
```
businesses (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  name         TEXT NOT NULL,
  description  TEXT,
  story        TEXT,
  category     TEXT NOT NULL,
  address      TEXT NOT NULL,
  phone        TEXT,
  website      TEXT,
  image_url    TEXT,
  is_approved  INTEGER DEFAULT 1,
  created_at   TEXT DEFAULT (datetime('now'))
)
```

## Tasks
- [x] Create `BusinessCreate` Pydantic model in `models.py`
- [x] Create `routers/businesses.py` with list, get, and create routes
- [x] Create `templates/register.html` with client-side validation
- [x] Add AI story writer button with loading state
- [x] Create `templates/index.html` with business grid and category filters
- [x] Create `templates/business.html` for full profile view
- [x] Seed 5 sample businesses in `database.py` on first run

## Notes
- `is_approved` defaults to `1` for the hackathon — in production this would be `0` with an admin review queue
- Category pills use `onclick` handlers with `filterCat()` JS function
- Business cards link directly to `/business/{id}`