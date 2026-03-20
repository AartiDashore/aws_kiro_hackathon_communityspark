"""
Author: Aarti Dashore
Version: 1.0.0

CommunitySpark MCP Server
Exposes two tools to Kiro:
  1. generate_business_story  — Story Writer Agent
  2. find_matching_businesses — Business Matchmaker Agent

Runs locally with Ollama (no API key needed).
Make sure Ollama is running: `ollama serve`
And the model is pulled: `ollama pull llama3`
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from mcp.server.fastmcp import FastMCP
import ollama
import aiosqlite

DB_PATH = os.path.join(os.path.dirname(__file__), "communityspark.db")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

mcp = FastMCP("CommunitySpark Agents")


async def fetch_businesses() -> list[dict]:
    """Pull all approved businesses from the local SQLite database."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT id, name, description, story, category, address, phone, website
               FROM businesses WHERE is_approved = 1 ORDER BY created_at DESC"""
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────────
# AGENT 1 — Story Writer
# ─────────────────────────────────────────────
@mcp.tool()
def generate_business_story(
    business_name: str,
    category: str,
    what_you_sell: str,
    your_background: str,
    neighborhood: str,
) -> str:
    """
    Generate a warm, authentic founder story for a minority-owned business listing.
    Returns a 3-sentence first-person story the owner can edit before publishing.
    """
    prompt = f"""Write a warm, authentic 3-sentence founder story for a community business listing.
Write in first person. Be genuine, personal, and community-focused. No clichés. No bullet points.

Business name: {business_name}
Category: {category}
What they sell/offer: {what_you_sell}
Owner background: {your_background or "not provided"}
Neighborhood/City: {neighborhood}

Output only the 3-sentence story. Nothing else."""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.8, "num_predict": 200},
    )
    return response["message"]["content"].strip()


# ─────────────────────────────────────────────
# AGENT 5 — Business Matchmaker
# ─────────────────────────────────────────────
@mcp.tool()
def find_matching_businesses(user_request: str) -> str:
    """
    Find the best minority-owned businesses that match a user's natural language request.
    Reads live data from the database and uses Ollama to reason about the best matches.
    """
    # Fetch live data synchronously inside the sync tool
    businesses = asyncio.run(fetch_businesses())

    if not businesses:
        return "No businesses are currently listed on CommunitySpark. Check back soon!"

    businesses_text = "\n".join(
        [
            f"ID:{b['id']} | {b['name']} | Category: {b['category']} | {b['description']} | {b['address']}"
            for b in businesses
        ]
    )

    prompt = f"""You are a friendly community guide for CommunitySpark, a platform for minority-owned local businesses.

A community member is looking for: "{user_request}"

Here are all the businesses currently listed:
{businesses_text}

Recommend the 1-3 best matches. For each match:
- State the business name
- Explain in one sentence exactly why it fits what they need
- Mention the address so they know where to go

If nothing is a good match, say so honestly and suggest what category to look for.
Be warm, specific, and conversational. Do not make up businesses that are not listed above."""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.5, "num_predict": 400},
    )
    return response["message"]["content"].strip()


if __name__ == "__main__":
    print(f"Starting CommunitySpark MCP server with model: {OLLAMA_MODEL}")
    print("Tools available: generate_business_story, find_matching_businesses")
    mcp.run(transport="stdio")
