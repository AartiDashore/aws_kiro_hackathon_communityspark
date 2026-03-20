# Spec: Flash Deals Engine

## Goal
Business owners post time-limited flash deals with a discount percentage
and expiry time. Visitors see a live feed with countdown timers.
Expired deals are deactivated automatically. Owners can edit or delete
deals after posting, adjust the remaining time, and set an urgency
threshold that triggers a sticky banner for customers.

## User Stories
- As a business owner, I can post a flash deal with title, description, discount %, original price, expiry in hours, and an optional urgency threshold
- As a business owner, I can edit a deal after posting — including title, description, discount, price, and time adjustment
- As a business owner, I can extend or shorten a deal's remaining time (positive hours = extend, negative = shorten)
- As a business owner, I can set an urgency threshold so a banner fires when X hours remain
- As a business owner, I can delete a deal manually at any time
- As a visitor, I can see all active deals sorted by newest first
- As a visitor, each deal shows a live countdown timer ticking in real time
- As a visitor, the timer turns red when under 1 hour remains
- As a visitor, I see a sticky urgency banner "⚡ Hurry up! Only Xh Ym remaining before [deal] expires!" when the threshold is crossed
- As a visitor, I can dismiss the urgency banner with a close button
- As a visitor, expired deals fade out without a page refresh

## Acceptance Criteria
- [x] Deals show live countdown timers updated every second
- [x] Timer color: amber when > 1 hour, red when < 1 hour, grey when expired
- [x] `deal_price` calculated server-side from `original_price` and `discount_percent`
- [x] Background task fires on deal creation to auto-expire after `expires_in_hours`
- [x] Expired deal cards fade to 40% opacity and become non-interactive
- [x] Deal modal on business profile page for posting new deals
- [x] Active deals shown inline on the business profile card with edit (✏️) and delete (🗑️) buttons
- [x] Edit modal pre-fills current deal values; hours field hidden, time-adjust field shown
- [x] `extend_hours` adjusts `expires_at` relative to current value; cannot shorten past current expiry
- [x] `urgency_threshold_hours` stored per deal; banner fires when `hoursLeft <= threshold`
- [x] Urgency banner is sticky below navbar, auto-refreshes every 60 seconds
- [x] If multiple deals have thresholds, the one closest to expiry wins the banner

## API Endpoints
- `GET    /api/deals` — all active non-expired deals with joined business info
- `POST   /api/deals` — create new deal, schedule background expiry task
- `PUT    /api/deals/{id}` — edit deal fields + optional `extend_hours` and `urgency_threshold_hours`
- `DELETE /api/deals/{id}` — manually expire a deal

## Data Model
```
deals (
  id                      INTEGER PRIMARY KEY AUTOINCREMENT,
  business_id             INTEGER REFERENCES businesses(id),
  title                   TEXT NOT NULL,
  description             TEXT,
  discount_percent        INTEGER,
  original_price          REAL,
  deal_price              REAL,
  expires_at              TEXT NOT NULL,
  is_active               INTEGER DEFAULT 1,
  urgency_threshold_hours REAL DEFAULT NULL,
  created_at              TEXT DEFAULT (datetime('now'))
)
```

## Pydantic Models
- `DealCreate` — required fields for new deal including `expires_in_hours` and optional `urgency_threshold_hours`
- `DealUpdate` — all fields optional; includes `extend_hours` (adjusts expiry) and `urgency_threshold_hours`

## Tasks
- [x] Create `DealCreate` and `DealUpdate` Pydantic models in `models.py`
- [x] Create `routers/deals.py` with list, create, update, and expire routes
- [x] Implement `expire_deal_after_delay()` background task using `asyncio.sleep`
- [x] Calculate `deal_price` server-side on creation
- [x] Handle `extend_hours` in PUT — fetch current `expires_at`, add delta, validate not in past
- [x] Store `urgency_threshold_hours` in DB on create and update
- [x] Create `templates/deals.html` with countdown timer JS
- [x] Add inline deal list + post/edit deal modal to `templates/business.html`
- [x] Add urgency banner element and `checkUrgencyBanner()` JS to business profile
- [x] Add urgency banner CSS (sticky, gradient, slide-in animation, dismiss button)
- [x] Seed 4 sample deals in `database.py` on first run

## Known Tradeoff
Background task expiry uses `asyncio.sleep` which does not survive server restarts.
For production, replace with APScheduler or a cron job that queries `expires_at < now()`.
