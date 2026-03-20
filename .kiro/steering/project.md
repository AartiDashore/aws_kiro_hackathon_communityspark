---
inclusion: always
---

# CommunitySpark — Project Steering

## What this project is

CommunitySpark is a local business discovery platform for minority-owned and community businesses. It lets owners register their business, post flash deals, and receive reviews. Customers can browse listings, get AI-powered recommendations, and find deals — all with zero external API dependencies.

## Tech stack

- Python 3.11, FastAPI, aiosqlite (SQLite), Jinja2
- Ollama for local LLM inference (llama3 / phi3 / llama3.2)
- Ruff for linting and formatting
- Vanilla JS, no frontend framework

## Project structure

- `main.py` — FastAPI app entry point, route registration, lifespan
- `models.py` — Pydantic request models
- `database.py` — SQLite init, schema, seed data
- `mcp_server.py` — MCP server exposing AI agents as Kiro tools
- `routers/businesses.py` — business CRUD
- `routers/deals.py` — flash deal creation and expiry
- `routers/reviews.py` — review submission
- `routers/agents.py` — AI agent HTTP endpoints (story writer + matchmaker)
- `templates/` — Jinja2 HTML pages
- `static/css/styles.css` — all styles

## Coding conventions

- All routers return `{"data": ..., "error": null}` on success
- Use `async/await` throughout — no blocking calls in route handlers
- Ruff is the linter and formatter — run `ruff check .` and `ruff format .` before committing
- Keep inline styles out of templates where possible; add CSS classes to `styles.css`
- Every new router file needs an `APIRouter()` instance and must be registered in `main.py`

## AI agents

- Agent 1 (Story Writer): `POST /api/agents/generate-story` — generates a founder story
- Agent 2 (Matchmaker): `POST /api/agents/match` — matches user request to live DB listings
- MCP tools mirror these agents for use inside Kiro: `generate_business_story`, `find_matching_businesses`
- Ollama must be running locally: `ollama serve` + `ollama pull llama3`
- Model is auto-detected; override with `OLLAMA_MODEL` env var

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Model to use for inference |

## What to avoid

- Do not add external API dependencies (no OpenAI, no Google Maps, no Supabase)
- Do not use blocking I/O in async route handlers
- Do not commit `communityspark.db` — it is auto-generated
