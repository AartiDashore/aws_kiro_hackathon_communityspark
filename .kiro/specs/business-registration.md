# Spec: Business Registration & Management

## Goal
Allow minority-owned business owners to self-register with their story,
category, location, contact info, and optional AI-generated founder story.
After registration, owners can edit their listing, upload/remove a photo,
and delete the business entirely from the profile page.

## User Stories
- As a business owner, I can register my business with name, description, story, category, address, phone, and website
- As a business owner, I can click "Write with AI" to generate a founder story from my basic inputs
- As a business owner, I can edit any field on my business profile after registration
- As a business owner, I can upload a photo for my listing (JPEG, PNG, WebP — max 5 MB)
- As a business owner, I can remove my uploaded photo; the card falls back to a category emoji
- As a business owner, I can delete my business listing (cascades to all deals and reviews)
- As a visitor, I can browse all approved businesses on the homepage
- As a visitor, I can filter businesses by category using pill buttons
- As a visitor, I can search businesses by name or description
- As a visitor, I can click a business card to see its full profile
- As a visitor, I see a category emoji placeholder when no photo has been uploaded

## Acceptance Criteria
- [x] Registration form validates all required fields before submission
- [x] Business saved to SQLite with `is_approved = 1` (auto-approved for hackathon)
- [x] Confirmation toast shown after successful registration
- [x] User redirected to new business profile page after 2 seconds
- [x] AI story writer calls `POST /api/agents/generate-story` with form data
- [x] Generated story populates the textarea and can be edited before submit
- [x] Business appears in homepage grid immediately after registration
- [x] Category filter pills filter the grid in real time
- [x] Edit modal pre-fills all current field values
- [x] Photo upload accepts JPEG, PNG, WebP, GIF — rejects other types with a clear error
- [x] Photo stored in `static/uploads/` with a unique filename (`{id}_{uuid}.{ext}`)
- [x] Photo delete removes the file from disk and clears `image_url` in the DB
- [x] Business cards show category emoji when `image_url` is NULL
- [x] Delete business requires confirmation and redirects to homepage on success

## API Endpoints
- `GET    /api/businesses` — list all approved businesses (supports `?category=` and `?search=`)
- `GET    /api/businesses/{id}` — single business with nested deals and reviews
- `POST   /api/businesses` — register new business
- `PUT    /api/businesses/{id}` — edit business fields (partial update)
- `DELETE /api/businesses/{id}` — delete business + cascade deals and reviews
- `POST   /api/businesses/{id}/image` — upload photo (multipart/form-data)
- `DELETE /api/businesses/{id}/image` — remove photo and delete file from disk

## Route Ordering Note
The `/image` sub-routes (`POST` and `DELETE`) must be registered **before**
`GET/PUT/DELETE /{business_id}` in `routers/businesses.py`. FastAPI matches
routes top-to-bottom and `/{business_id}` would otherwise swallow
`/{business_id}/image` with a 405.

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
- `BusinessUpdate` — all fields optional, used for partial PUT updates

## Tasks
- [x] Create `BusinessCreate` and `BusinessUpdate` Pydantic models in `models.py`
- [x] Create `routers/businesses.py` with list, get, create, update, delete, image upload, image delete routes
- [x] Register `/image` routes before `/{business_id}` to avoid 405 routing conflict
- [x] Create `templates/register.html` with client-side validation
- [x] Add AI story writer button with loading state
- [x] Create `templates/index.html` with business grid and category filters
- [x] Create `templates/business.html` for full profile view with edit/delete/upload UI
- [x] Add category emoji fallback in both card grid and profile page
- [x] Seed 5 sample businesses in `database.py` on first run

## Notes
- `is_approved` defaults to `1` for the hackathon — in production this would be `0` with an admin review queue
- Uploaded files are served via FastAPI's `StaticFiles` mount at `/static`
- `static/uploads/` is created automatically on startup via `os.makedirs(..., exist_ok=True)`
