# Spec: AI Agents

## Goal
Two AI-powered agents that use Ollama (local LLM) to add intelligence
to the platform — one for generating founder stories, one for matching
users to businesses. Both exposed as MCP tools for use inside Kiro.

## Agent 1: Story Writer

### User Story
As a business owner filling out the registration form, I can click
"Write with AI" to auto-generate a warm 3-sentence founder story
from my name, category, description, and optional background.

### Acceptance Criteria
- [x] Button appears inline next to the "Your Story" label
- [x] Shows loading state while AI writes ("✨ Writing…")
- [x] Generated story populates the textarea and is fully editable
- [x] On error, shows specific message (timeout, Ollama not running, etc.)
- [x] Endpoint: `POST /api/agents/generate-story`

### Prompt Design (v4 — final)
```
Write a warm, authentic 3-sentence founder story for a community
business listing. Write in first person. Be genuine, personal, and
community-focused. No bullet points.

Business name: {name}
Category: {category}
What they sell: {what_you_sell}
Owner background: {background}
Location: {neighborhood}

Output ONLY the 3-sentence story. Start immediately.
```
Iterations 1-3 produced generic output. Adding "Output ONLY" and
"Start immediately" stopped the model from adding preamble.

---

## Agent 2: Business Matchmaker

### User Story
As a visitor on the homepage, I can type a natural language request
like "I need a haircut for natural hair" and get relevant business
recommendations in plain English.

### Acceptance Criteria
- [x] Chat widget on homepage with quick-ask chips
- [x] Python keyword filtering runs BEFORE calling LLM
- [x] AI only sees businesses in relevant categories
- [x] Response is focused — no hallucinated connections
- [x] Endpoint: `POST /api/agents/match`
- [x] Loading spinner shown while AI processes

### Category Keyword Map (Python-side filter)
```python
"Beauty & Wellness": ["hair", "haircut", "salon", "curl", "braids", ...]
"Food & Dining":     ["food", "eat", "restaurant", "lunch", ...]
"Retail":            ["shop", "buy", "gift", "spice", "market", ...]
"Arts & Culture":    ["book", "art", "music", "gallery", ...]
"Services":          ["tailor", "alter", "sew", "repair", ...]
```
This solved the hallucination problem — the model cannot recommend
a tailor for a haircut request because it never sees the tailor.

---

## MCP Integration

Both agents are exposed as tools in `mcp_server.py` via `fastmcp`:

```python
@mcp.tool()
def generate_business_story(business_name, category, ...) -> str

@mcp.tool()
def find_matching_businesses(user_request) -> str
```

Registered in `.kiro/mcp.json`:
```json
{
  "mcpServers": {
    "communityspark-agents": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": { "OLLAMA_MODEL": "llama3" }
    }
  }
}
```

## Tasks
- [x] Create `routers/agents.py` with both endpoints
- [x] Create `mcp_server.py` with both MCP tools
- [x] Add `GET /api/agents/status` diagnostic endpoint
- [x] Add keyword filter map in Python for matchmaker
- [x] Wire AI story writer button in `templates/register.html`
- [x] Build matchmaker chat widget in `templates/index.html`
- [x] Add loading spinner CSS to `styles.css`