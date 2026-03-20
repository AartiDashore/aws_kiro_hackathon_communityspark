# Building CommunitySpark — The Journey

This document captures the build process, decisions made, what worked, and what didn't. Written for transparency and to help others learn from this project.

---

## The Problem

Minority-owned and community businesses are often invisible online. Platforms like Yelp and Google Maps exist, but they require business owners to navigate complex setups, pay for visibility, and compete against large chains with marketing budgets. There's no dedicated space that centers community businesses, tells their stories, and helps locals find them without algorithmic bias.

CommunitySpark was built to fill that gap — a zero-friction platform where any community business can list themselves, share their story, post deals, and get discovered.

---

## How Kiro Was Used

### Chat
Used throughout the build for:
- Debugging async SQLite connection handling
- Fixing Jinja2 template rendering issues
- Refining the AI prompt engineering for the story writer agent
- Getting the MCP server wired up correctly with `fastmcp`

### Steering
A steering file (`.kiro/steering/project.md`) was added to keep Kiro aligned with the project's conventions — no external APIs, async-first code, consistent router response shapes. This meant every suggestion Kiro made stayed within the project's constraints without needing to re-explain them each time.

### Hooks
A Ruff lint hook (`.kiro/hooks/ruff-on-save.json`) was added so that every time a Python file is saved, Kiro automatically checks for lint and formatting issues. This kept the codebase clean without manual intervention.

### MCP
The MCP server (`mcp_server.py`) exposes both AI agents as tools directly inside Kiro:
- `generate_business_story` — lets Kiro generate a founder story on demand
- `find_matching_businesses` — lets Kiro query the live database and recommend businesses

This was one of the most interesting parts of the build. Having Kiro able to call into the app's own database and AI layer felt like a genuine workflow innovation.

---

## Architecture Decisions

### Why SQLite?
No setup, no credentials, no running service. The database is a single file that gets created on first run. For a community tool that needs to be easy to self-host, this was the right call. The tradeoff is that it doesn't scale horizontally — but that's a problem for later.

### Why Ollama?
The whole point of CommunitySpark is zero external dependencies. Using OpenAI or Anthropic would mean API keys, costs, and a dependency on a third-party service. Ollama runs locally, works offline, and supports multiple models. The app auto-detects whatever model is installed.

### Why Vanilla JS?
React or Vue would add build tooling, node_modules, and complexity that isn't needed here. The UI is server-rendered Jinja2 with a thin JS layer for interactivity. It loads fast, works on older devices, and is easy to read.

### Why FastAPI?
Async-first, automatic OpenAPI docs at `/docs`, Pydantic validation built in. It was the obvious choice for a Python API that needed to be clean and well-documented.

---

## What Worked Well

- **AI story writer on the registration form** — this was the feature that felt most impactful. Business owners often struggle to write about themselves. Having AI generate a warm, first-person story from a few fields lowered the barrier significantly.
- **Category-filtered matchmaker** — filtering businesses in Python before sending to the LLM meant the AI couldn't hallucinate businesses that don't exist. This was a deliberate design choice that made the agent much more reliable.
- **Zero-dependency setup** — the 3-command setup (venv, pip install, uvicorn) worked exactly as intended. No `.env` files, no external services, no surprises.
- **Auto-seeding sample data** — having 5 businesses, 4 deals, and 5 reviews ready on first run made demos and testing much smoother.
- **MCP integration** — wiring the agents into Kiro via MCP was straightforward with `fastmcp` and added a genuinely useful workflow.

---

## What Didn't Work / Tradeoffs

- **No authentication** — anyone can post deals or reviews. This was a conscious tradeoff for simplicity, but it's the first thing that would need to change for a real deployment. A simple token-based system or OAuth would work.
- **Ollama cold start** — the first AI request after starting Ollama can take 10–30 seconds while the model loads. This surprised users during demos. A `/api/agents/status` endpoint was added to let the UI warn users, but a proper loading state in the frontend would be better.
- **Inline styles in templates** — early in the build, styles were added inline for speed. This made the HTML harder to read and maintain. The steering file now enforces moving styles to `styles.css`, but some inline styles remain.
- **No pagination** — all businesses load at once. Fine for a demo with 5 businesses, but would need pagination or virtual scrolling for real-world use.
- **Deal expiry via background task** — deals expire via an `asyncio.sleep` background task. This works but doesn't survive server restarts. A proper scheduler (APScheduler or a cron job) would be more reliable.

---

## What's Next

If this project were to grow beyond a hackathon:

1. Add lightweight auth (JWT or session-based) so only verified owners can post deals
2. Replace the background task expiry with a proper scheduler
3. Add pagination to the business listing
4. Add a map view (Leaflet.js — no API key needed)
5. Add business hours and availability
6. Build a moderation queue for new registrations
7. Package as a Docker container for easy community self-hosting

---

## Lessons Learned

- Kiro's steering files are genuinely useful for keeping a consistent coding style across a multi-file project. Setting them up early saves a lot of back-and-forth.
- Local LLMs via Ollama are production-viable for simple generation tasks. The quality of `llama3` for short-form creative writing (founder stories) was better than expected.
- Prompt engineering matters more than model size for constrained tasks. The story writer prompt went through 4 iterations before the output was consistently good.
- Building with zero external dependencies forces creative solutions that often end up being better anyway.
