# CommunitySpark 🌍
### A discovery platform for minority-owned and community businesses

[![CI](https://github.com/AartiDashore/aws_kiro_hackathon_communityspark/actions/workflows/ci.yml/badge.svg)](https://github.com/AartiDashore/aws_kiro_hackathon_communityspark/actions/workflows/ci.yml)

> "68% of minority-owned small businesses report that limited visibility and lack of digital presence are their biggest barriers to growth." — U.S. Senate Committee on Small Business & Entrepreneurship

---

## The Problem

Minority-owned and community businesses are systematically invisible on mainstream platforms. Yelp and Google Maps bury small businesses without ad budgets. There is no dedicated space that centers their stories, amplifies their deals, and connects them with locals who genuinely want to support them.

**Target users:**
- **Business owners** — independent, minority-owned, and community businesses who need visibility without complexity or cost
- **Community members** — locals who want to discover and support businesses that reflect their neighborhood

---

## Solution

A zero-friction web platform with three core loops:

1. **Discovery** — browse, filter, and AI-match businesses by category or natural language query
2. **Deals** — post and discover time-limited flash deals with live countdown timers
3. **Stories** — every business has a founder story; AI helps write it so the barrier to listing is as low as possible

### Key Features

| Feature | Description |
|---------|-------------|
| Business registry | Self-registration with story, category, address, photo, and contact info |
| Flash deals | Time-limited discounts with live countdown timers and auto-expiry |
| Reviews | Star ratings and comments to build community trust |
| AI Story Writer | Generates a warm first-person founder story from basic inputs |
| AI Matchmaker | Natural language search — "I need a haircut for natural hair" → Crown & Glory Salon |
| Business management | Edit, photo upload/removal, delete — all from the profile page |
| MCP server | Both AI agents exposed as tools inside Kiro |
| Auto-seeded data | 5 businesses, 4 deals, 5 reviews on first run — no manual setup |

---

## Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
uvicorn main:app --reload
```

Open **http://localhost:8000** — 5 sample businesses, 4 deals, and 5 reviews load automatically on first run. No `.env` file needed. No external services.

### For AI features (optional but recommended)
```bash
# Install Ollama from https://ollama.com then:
ollama pull phi3
```

---

## Pages

| URL | Description |
|-----|-------------|
| `http://localhost:8000` | Home — browse businesses + AI matchmaker |
| `http://localhost:8000/deals` | Flash deals with live countdown timers |
| `http://localhost:8000/register` | Register a new business |
| `http://localhost:8000/business/1` | Example business profile |
| `http://localhost:8000/api/agents/status` | Check AI + Ollama status |
| `http://localhost:8000/docs` | Auto-generated API docs |

---

## Architecture

```
communityspark/
├── main.py                  # FastAPI app, route registration, lifespan
├── database.py              # SQLite init, schema, seed data
├── models.py                # Pydantic request/response models
├── mcp_server.py            # MCP server — AI agents as Kiro tools
├── routers/
│   ├── businesses.py        # Business CRUD + image upload/delete
│   ├── deals.py             # Flash deals + edit + time extension + expiry
│   ├── reviews.py           # Review submission and retrieval
│   └── agents.py            # AI story writer + matchmaker endpoints
├── templates/               # Jinja2 HTML pages
├── static/
│   ├── css/styles.css       # All CSS — no framework
│   └── uploads/             # Uploaded business photos (auto-created, not committed)
└── .kiro/
    ├── steering/project.md  # Project conventions for Kiro
    ├── specs/               # Feature specs (business reg, deals, AI agents)
    ├── hooks/               # Automation hooks (ruff, deal expiry check)
    └── mcp.json             # MCP server config
```

### How the AI matchmaker works

```
User: "I need a haircut for natural hair"
         ↓
Python keyword matching → identifies "Beauty & Wellness"
         ↓
Filters SQLite DB → only beauty businesses sent to AI
         ↓
Ollama (local LLM) → picks best match from filtered list
         ↓
"Crown & Glory Salon — specializes in natural hair care for all textures"
```

Key decision: **Python filters first, AI reasons second.** This prevents hallucination.

---

## API Reference

All endpoints are prefixed with `/api`. Full interactive docs at `/docs` when the server is running.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/businesses` | List all businesses (supports `?category=` and `?search=`) |
| `POST` | `/api/businesses` | Register a new business |
| `GET` | `/api/businesses/{id}` | Get a business with its deals and reviews |
| `PUT` | `/api/businesses/{id}` | Edit business fields (partial update) |
| `DELETE` | `/api/businesses/{id}` | Delete a business and all its deals and reviews |
| `POST` | `/api/businesses/{id}/image` | Upload a business photo (JPEG/PNG/WebP, max 5 MB) |
| `DELETE` | `/api/businesses/{id}/image` | Remove the business photo |
| `POST` | `/api/deals` | Post a flash deal |
| `GET` | `/api/deals` | List all active non-expired deals |
| `PUT` | `/api/deals/{id}` | Edit a deal (title, discount, time extension, urgency threshold) |
| `DELETE` | `/api/deals/{id}` | Expire/remove a deal |
| `POST` | `/api/reviews` | Submit a review |
| `GET` | `/api/agents/status` | Check Ollama status and installed models |
| `POST` | `/api/agents/generate-story` | AI: generate a founder story |
| `POST` | `/api/agents/match` | AI: find businesses matching a natural language request |

---

## Business Management

From any business profile page, owners can:

- Edit all fields (name, description, story, category, address, phone, website) via the ✏️ Edit button
- Upload a photo (JPEG, PNG, WebP — max 5 MB) stored in `static/uploads/`
- Remove the uploaded photo — cards fall back to a category emoji automatically
- Delete the business entirely — cascades to all associated deals and reviews

## Flash Deals

- Post a deal with title, discount %, original price, and expiry in hours
- Edit a deal after posting — title, description, discount, price, and time
- Extend or shorten remaining time using the `extend_hours` field (positive = extend, negative = shorten)
- Set an urgency threshold: when X hours remain, a sticky dismissible banner fires at the top of the page
- Delete a deal manually at any time

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Model to use (auto-detected if not set) |

---

## Design Decisions & Trade-offs

| Decision | Reason | Trade-off |
|----------|--------|-----------|
| **SQLite** over Supabase/Postgres | Zero setup, single file, auto-created on first run | Doesn't scale horizontally; swap to Postgres for multi-server deployments |
| **Ollama** over OpenAI/Anthropic | No API key, no cost, fully local, works offline | Cold start delay of 10–30s on first request |
| **Vanilla JS** over React/Vue | No build step, no node_modules, loads fast on older devices | Less component reuse; acceptable for this scope |
| **FastAPI** over Flask/Django | Async-first, auto `/docs`, Pydantic validation built in | Smaller ecosystem than Django |
| **Python-first AI filtering** | Filters DB in Python before calling LLM — prevents hallucination | Requires maintaining the keyword map as categories grow |

### Security notes
- No authentication in this version — deliberate hackathon trade-off. In production: JWT or session-based auth.
- File uploads: MIME type checked server-side; files over 5 MB rejected; UUID-based filenames prevent path traversal.
- All queries use parameterised statements via `aiosqlite` — no SQL injection.
- All user content HTML-escaped via `escHtml()` in JS before rendering.

---

## How Kiro Was Used

| Feature | How it was used |
|---------|----------------|
| **AI Chat** | Debugging async SQLite handling; fixing Jinja2 template issues; iterating on AI prompts; resolving 405 route ordering errors |
| **Steering** | `.kiro/steering/project.md` enforced no external APIs, async-first code, consistent response shapes, and route ordering rules across the entire build |
| **Hooks** | `ruff-on-save.json` — auto-runs `ruff check` on every Python save; `deal-expiry-check.json` — verifies background task is wired on every edit to `deals.py` |
| **Specs** | Three full specs written before coding: business registration, deals engine, AI agents — each with user stories, acceptance criteria, data models, and task checklists |
| **MCP** | `mcp_server.py` exposes both AI agents (`generate_business_story`, `find_matching_businesses`) as tools callable directly from inside Kiro |

---

## Learning Journey

### What worked
- **Steering files on day one** — the single biggest productivity unlock. Every Kiro suggestion stayed within the project's constraints automatically.
- **Spec before code** — writing acceptance criteria upfront felt slow. It wasn't. Implementations matched specs closely on the first attempt.
- **Python-first AI filtering** — the matchmaker initially hallucinated connections between unrelated businesses. Moving category filtering into Python before the LLM call solved it completely.
- **Local LLMs for short-form creative writing** — Ollama's quality for founder stories was better than expected. Warm and personal, not generic.

### What didn't work
- **Streaming AI responses** — SSE streaming added complexity without improving reliability. Switched to standard JSON responses.
- **`asyncio.sleep` for deal expiry** — works during a session but doesn't survive server restarts.
- **Inline styles in templates** — accumulated early and made templates hard to read. Steering now enforces `styles.css`.
- **FastAPI `redirect_slashes`** — the default 307 redirect on trailing slashes drops POST bodies. Fixed by setting `redirect_slashes=False` on the app.

---

## What's Next

- [ ] Lightweight JWT auth for verified business owners
- [ ] Map view with Leaflet.js (no API key needed)
- [ ] Pagination for large business listings
- [ ] APScheduler to replace `asyncio.sleep` deal expiry
- [ ] Docker container for one-command community self-hosting
- [ ] Admin moderation queue for new business registrations

---

## CI/CD

GitHub Actions runs on every push and pull request to `main`:

1. **Lint** — `ruff check .` and `ruff format --check .`
2. **Deploy** — runs after lint passes on pushes to `main`

See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

---

## Screenshots

### Homepage — Business Discovery + AI Matchmaker
![Homepage](screenshots/homepage_1.png)

### Business Listings with Categories
![Listings](screenshots/homepage_2.png)

### Flash Deals with Live Countdown Timers
![Deals](screenshots/deals_1.png)

### Register a Business with AI Story Writer
![Register](screenshots/listing_1.png)

### Business Profile with Reviews
![Profile](screenshots/listing_2.png)

---

## Sample Data

On first run the database seeds automatically with:
- 5 community businesses across Food, Beauty, Arts, Services, and Retail
- 4 active flash deals with expiry times
- 5 reviews across multiple businesses

The SQLite file (`communityspark.db`) is created automatically — no setup required.

---

## Build Journey

See [BUILDING.md](BUILDING.md) for the full process — decisions made, what worked, what failed, and lessons learned.

---

## .kiro Directory

```
.kiro/
├── steering/
│   └── project.md          # Project-wide conventions loaded into every Kiro session
├── specs/
│   ├── business-registration.md
│   ├── deals-engine.md
│   └── ai-agents.md
├── hooks/
│   ├── ruff-on-save.json
│   └── deal-expiry-check.json
└── mcp.json                # MCP server config for Kiro
```

---

## License

[MIT](LICENSE)

Disclaimer: This project was developed for the Amazon Hackathon by Aarti Dashore. Any use, modification, or distribution of this code outside the hackathon must include proper attribution to Aarti Dashore. By using this repository, you agree to give appropriate credit.

Please credit as: “Project by Aarti Dashore (GitHub: AartiDashore)”

Youtube Link: https://youtu.be/9AAc76r9IJM
