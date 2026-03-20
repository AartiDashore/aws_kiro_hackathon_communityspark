"""
Author: Aarti Dashore
Version: 1.0.0

Agent routes — filters businesses in Python by category BEFORE sending to AI.
AI only sees relevant businesses, so it cannot recommend unrelated ones.
"""

import os
import httpx
from database import get_db
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

router = APIRouter()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Keywords in the user query mapped to relevant business categories
CATEGORY_KEYWORDS = {
    "Beauty & Wellness": [
        "hair",
        "haircut",
        "salon",
        "cut",
        "style",
        "natural hair",
        "curl",
        "braids",
        "locs",
        "weave",
        "beauty",
        "nails",
        "skin",
        "spa",
        "massage",
        "wax",
        "eyebrow",
        "makeup",
        "barber",
        "shave",
    ],
    "Food & Dining": [
        "food",
        "eat",
        "restaurant",
        "lunch",
        "dinner",
        "breakfast",
        "meal",
        "cook",
        "cuisine",
        "dish",
        "hungry",
        "drink",
        "coffee",
        "cafe",
        "taco",
        "pizza",
        "sushi",
        "bbq",
        "vegan",
        "snack",
        "dessert",
        "bakery",
    ],
    "Retail": [
        "shop",
        "buy",
        "store",
        "gift",
        "purchase",
        "spice",
        "grocery",
        "ingredient",
        "product",
        "item",
        "market",
        "goods",
    ],
    "Arts & Culture": [
        "book",
        "art",
        "music",
        "culture",
        "gallery",
        "craft",
        "creative",
        "painting",
        "sculpture",
        "poetry",
        "literature",
        "read",
    ],
    "Services": [
        "tailor",
        "alter",
        "sew",
        "fix",
        "repair",
        "clean",
        "legal",
        "tax",
        "finance",
        "consult",
        "service",
        "help",
        "support",
    ],
}


def get_relevant_categories(query: str) -> list[str]:
    """Return categories that match keywords in the user query."""
    query_lower = query.lower()
    matched = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            matched.append(category)
    return matched


async def get_installed_model() -> str:
    """Auto-detect the first available model from Ollama."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            res = await client.get(f"{OLLAMA_URL}/api/tags")
            models = res.json().get("models", [])
            if models:
                return models[0]["name"]
    except Exception:
        pass
    return OLLAMA_MODEL


async def ask_ollama(prompt: str, temperature: float = 0.3) -> str:
    """Send a prompt to Ollama and return the response text."""
    model = await get_installed_model()
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            res = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": 200,
                    },
                },
            )
            res.raise_for_status()
            return res.json().get("response", "").strip()
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, detail="Ollama timed out. Try again in 30 seconds."
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503, detail="Cannot connect to Ollama at localhost:11434."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")


# ── Request models ──────────────────────────────────────────────


class StoryRequest(BaseModel):
    business_name: str
    category: str
    what_you_sell: str
    neighborhood: str
    your_background: Optional[str] = ""


class MatchRequest(BaseModel):
    message: str


# ── Diagnostic ─────────────────────────────────────────────────


@router.get("/status")
async def agent_status():
    """Check Ollama status and installed models."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            res = await client.get(f"{OLLAMA_URL}/api/tags")
            models = [m["name"] for m in res.json().get("models", [])]
            return {
                "ollama": "running",
                "models_installed": models,
                "will_use": models[0] if models else "none — run: ollama pull phi3",
            }
    except Exception as e:
        return {"ollama": "unreachable", "error": str(e)}


# ── Agent 1: Story Writer ───────────────────────────────────────


@router.post("/generate-story")
async def generate_story(req: StoryRequest):
    """Agent 1 — generate a founder story from basic business info."""
    prompt = f"""Write a warm, authentic 3-sentence founder story for a community business listing.
Write in first person. Be genuine, personal, and community-focused. No bullet points.

Business name: {req.business_name}
Category: {req.category}
What they sell: {req.what_you_sell}
Owner background: {req.your_background or "not provided"}
Location: {req.neighborhood}

Output ONLY the 3-sentence story. Start immediately. Nothing else."""

    story = await ask_ollama(prompt, temperature=0.7)
    return {"story": story, "error": None}


# ── Agent 5: Business Matchmaker ───────────────────────────────


@router.post("/match")
async def match_businesses(req: MatchRequest):
    """
    Agent 5 — match businesses to a user request.
    Filters by category in Python first, then sends only relevant
    businesses to the AI so it cannot recommend unrelated ones.
    """
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT id, name, description, category, address
               FROM businesses WHERE is_approved = 1 ORDER BY created_at DESC"""
        )
        rows = await cursor.fetchall()
        all_businesses = [dict(r) for r in rows]
    finally:
        await db.close()

    if not all_businesses:
        return {
            "reply": "No businesses are listed yet. Be the first to register!",
            "error": None,
        }

    # ── Python-side filtering — AI never sees irrelevant businesses ──
    relevant_categories = get_relevant_categories(req.message)

    if relevant_categories:
        filtered = [b for b in all_businesses if b["category"] in relevant_categories]
    else:
        # Query is too vague — show everything
        filtered = all_businesses

    # No matches found at all — return immediately without calling AI
    if not filtered:
        category_list = (
            ", ".join(relevant_categories) if relevant_categories else "any category"
        )
        return {
            "reply": f"I don't see any {category_list} businesses listed yet. "
            f"Try browsing all categories or check back soon as new businesses join!",
            "error": None,
        }

    businesses_text = "\n".join(
        [f"- {b['name']}: {b['description']} | {b['address']}" for b in filtered]
    )

    prompt = f"""You are a helpful community guide for CommunitySpark.

Someone is looking for: "{req.message}"

Relevant businesses available:
{businesses_text}

From this list, recommend the best match(es). For each one:
- State the business name
- One sentence explaining why it fits
- The address

Keep your answer short and focused. Only mention businesses from the list above."""

    reply = await ask_ollama(prompt, temperature=0.3)
    return {"reply": reply, "error": None}
