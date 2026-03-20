# Spec: Flash Deals Engine

## Goal
Business owners post time-limited flash deals with a discount percentage
and expiry time. Visitors see a live feed with countdown timers.
Expired deals are deactivated automatically.

## User Stories
- As a business owner, I can post a flash deal with title, description, discount %, original price, and expiry time in hours
- As a visitor, I can see all active deals sorted by newest first
- As a visitor, each deal shows a live countdown timer ticking in real time
- As a visitor, the timer turns red when under 1 hour remains
- As a visitor, expired deals fade out without a page refresh
- As a business owner, I can post a deal directly from the business profile page
- As a business owner, I can edit an existing deal's title, description, discount, and price
- As a business owner, I can extend or shorten a deal's expiry time by specifying a positive or negative hour delta
- As a business owner, I can set an urgency threshold (in hours) so a sticky banner appears when the deal is close to expiring
- As a business owner, I can delete a deal from the business profile page

## Acceptance Criteria
- [x] Deals show live countdown timers updated every second
- [x] Timer color: amber when > 1 hour, red when < 1 hour, grey when expired
- [x] `deal_price` calculated server-side from `original_price` and `discount_percent`
- [x] Background task fires on deal creation to auto-expire after `expires_in_hours`
- [x] Expired deal cards fade to 40% opacity and become non-interactive
- [x] Deal modal on business profile page for posting new deals
- [x] Active deals shown inline on the business profile card
- [x] Edit deal modal pre-fills current values and saves via `PUT /api/deals/{id}`
- [x] `extend_hours` field in edit modal adjusts expiry; positive extends, negative shortens; result cannot be in the past
- [x] `urgency_threshold_hours` can be set on create or edit; stored in DB
- [x] Sticky urgency banner fires when `hoursLeft <= urgency_threshold_hours`, auto-refreshes every 60 s, is dismissible
- [x] Delete button on each deal card calls `DELETE /api/deals/{id}` and removes the card from the DOM

## API Endpoints
- `GET    /api/deals` — all active non-expired deals with joined business info
- `POST   /api/deals` — create new deal, schedule background expiry task
- `PUT    /api/deals/{id}` — edit deal fields and/or adjust expiry via `extend_hours`
- `DELETE /api/deals/{id}` — manually expire a deal

## Data Model
```
deals (
  id                     INTEGER PRIMARY KEY AUTOINCREMENT,
  business_id            INTEGER REFERENCES businesses(id),
  title                  TEXT NOT NULL,
  description            TEXT,
  discount_percent       INTEGER,
  original_price         REAL,
  deal_price             REAL,
  expires_at             TEXT NOT NULL,
  is_active              INTEGER DEFAULT 1,
  urgency_threshold_hours REAL DEFAULT NULL,
  created_at             TEXT DEFAULT (datetime('now'))
)
```

## Pydantic Models
- `DealCreate` — required fields for new deal, includes optional `urgency_threshold_hours`
- `DealUpdate` — all fields optional; `extend_hours` (float) adjusts expiry duration; `urgency_threshold_hours` updates threshold

## Tasks
- [x] Create `DealCreate` Pydantic model in `models.py`
- [x] Create `routers/deals.py` with list, create, and expire routes
- [x] Implement `expire_deal_after_delay()` background task using `asyncio.sleep`
- [x] Calculate `deal_price` server-side on creation
- [x] Create `templates/deals.html` with countdown timer JS
- [x] Add deal count badge to business cards on homepage
- [x] Add inline deal list + post deal modal to `templates/business.html`
- [x] Seed 4 sample deals in `database.py` on first run
- [x] Add `urgency_threshold_hours` column to `deals` table in `database.py`
- [x] Add `DealUpdate` model to `models.py`
- [x] Add `PUT /{id}` edit route to `routers/deals.py` with `extend_hours` logic
- [x] Add edit deal modal with "Adjust time" and urgency threshold fields to `templates/business.html`
- [x] Add delete button per deal card to `templates/business.html`
- [x] Add `.urgency-banner` CSS with slide-in animation and close button to `styles.css`

## Known Tradeoff
Background task expiry uses `asyncio.sleep` which does not survive server restarts.
For production, replace with APScheduler or a cron job that queries `expires_at < now()`.