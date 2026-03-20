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
- As a business owner, I can edit my business name, description, story, category, address, phone, and website after registration
- As a business owner, I can upload a photo for my business listing (JPEG, PNG, WebP, or GIF, max 5 MB)
- As a business owner, I can remove my uploaded photo; the listing falls back to a category emoji
- As a business owner, I can delete my business listing, which also removes all associated deals and reviews

## Acceptance Criteria
- [x] Registration form validates all required fields before submission
- [x] Business saved to SQLite with `is_approved = 1` (auto-approved for hackathon)
- [x] Confirmation toast shown after successful registration
- [x] User redirected to new business profile page after 2 seconds
- [x] AI story writer calls `POST /api/agents/generate-story` with form data
- [x] Generated story populates the textarea and can be edited before submit
- [x] Business appears in homepage grid immediately after registration
- [x] Category filter pills filter the grid in real time
- [x] Edit modal pre-fills all current business fields and saves via `PUT /api/businesses/{id}`
- [x] Image upload validates MIME type (JPEG/PNG/WebP/GIF) and rejects files over 5 MB
- [x] Uploaded photo stored in `static/uploads/` with UUID-based filename to avoid collisions
- [x] Removing a photo deletes the file from disk and clears `image_url` in the DB
- [x] When no photo is present, business profile shows a large category emoji on a dark background
- [x] Deleting a business cascades to remove all its deals and reviews

## API Endpoints
- `GET    /api/businesses` — list all approved businesses (supports `?category=` and `?search=`)
- `GET    /api/businesses/{id}` — single business with nested deals and reviews
- `POST   /api/businesses` — register new business
- `PUT    /api/businesses/{id}` — edit business fields (`BusinessUpdate` model — all fields optional)
- `DELETE /api/businesses/{id}` — delete business and cascade deals/reviews
- `POST   /api/businesses/{id}/image` — upload photo (multipart/form-data, max 5 MB)
- `DELETE /api/businesses/{id}/image` — remove photo from disk and clear `image_url`

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

## Pydantic Models
- `BusinessCreate` — all required fields for registration
- `BusinessUpdate` — all fields optional; used by `PUT /{id}`

## Tasks
- [x] Create `BusinessCreate` Pydantic model in `models.py`
- [x] Create `routers/businesses.py` with list, get, and create routes
- [x] Create `templates/register.html` with client-side validation
- [x] Add AI story writer button with loading state
- [x] Create `templates/index.html` with business grid and category filters
- [x] Create `templates/business.html` for full profile view
- [x] Seed 5 sample businesses in `database.py` on first run
- [x] Add `BusinessUpdate` model to `models.py`
- [x] Add `PUT /{id}` edit route to `routers/businesses.py`
- [x] Add `DELETE /{id}` delete route with cascade to `routers/businesses.py`
- [x] Add `POST /{id}/image` upload route (registered before `/{id}` catch-all)
- [x] Add `DELETE /{id}/image` remove route (registered before `/{id}` catch-all)
- [x] Add edit modal, image upload modal, and delete buttons to `templates/business.html`
- [x] Add category emoji fallback (`CAT_EMOJI` map) to `templates/business.html`
- [x] Add `.profile-photo-wrap`, `.profile-photo-wrap--default`, `.profile-photo-default` CSS

## Notes
- `is_approved` defaults to `1` for the hackathon — in production this would be `0` with an admin review queue
- Category pills use `onclick` handlers with `filterCat()` JS function
- Business cards link directly to `/business/{id}`
- Sub-routes `/{id}/image` must be registered before `/{id}` in the router to avoid 405 errors