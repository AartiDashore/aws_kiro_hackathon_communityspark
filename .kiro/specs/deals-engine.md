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

## Acceptance Criteria
- [x] Deals show live countdown timers updated every second
- [x] Timer color: amber when > 1 hour, red when < 1 hour, grey when expired
- [x] `deal_price` calculated server-side from `original_price` and `discount_percent`
- [x] Background task fires on deal creation to auto-expire after `expires_in_hours`
- [x] Expired deal cards fade to 40% opacity and become non-interactive
- [x] Deal modal on business profile page for posting new deals
- [x] Active deals shown inline on the business profile card

## API Endpoints
- `GET    /api/deals` — all active non-expired deals with joined business info
- `POST   /api/deals` — create new deal, schedule background expiry task
- `DELETE /api/deals/{id}` — manually expire a deal

## Data Model
```
deals (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  business_id      INTEGER REFERENCES businesses(id),
  title            TEXT NOT NULL,
  description      TEXT,
  discount_percent INTEGER,
  original_price   REAL,
  deal_price       REAL,
  expires_at       TEXT NOT NULL,
  is_active        INTEGER DEFAULT 1,
  created_at       TEXT DEFAULT (datetime('now'))
)
```

## Tasks
- [x] Create `DealCreate` Pydantic model in `models.py`
- [x] Create `routers/deals.py` with list, create, and expire routes
- [x] Implement `expire_deal_after_delay()` background task using `asyncio.sleep`
- [x] Calculate `deal_price` server-side on creation
- [x] Create `templates/deals.html` with countdown timer JS
- [x] Add deal count badge to business cards on homepage
- [x] Add inline deal list + post deal modal to `templates/business.html`
- [x] Seed 4 sample deals in `database.py` on first run

## Known Tradeoff
Background task expiry uses `asyncio.sleep` which does not survive server restarts.
For production, replace with APScheduler or a cron job that queries `expires_at < now()`.