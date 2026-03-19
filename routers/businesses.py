"""
Implementing businesses router with CRUD endpoints
Author: Aarti Dashore
Version: 1.0.0
"""
from fastapi import APIRouter, HTTPException
from models import BusinessCreate
from database import get_db

router = APIRouter()


@router.get("/")
async def list_businesses(category: str = None, search: str = None):
    """Return all approved businesses with optional filters."""
    db = await get_db()
    try:
        query = "SELECT * FROM businesses WHERE is_approved = 1"
        params = []
        if category:
            query += " AND category = ?"
            params.append(category)
        if search:
            query += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        query += " ORDER BY created_at DESC"
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return {"data": [dict(r) for r in rows], "error": None}
    finally:
        await db.close()


@router.get("/{business_id}")
async def get_business(business_id: int):
    """Return a single business with its deals and reviews."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM businesses WHERE id = ? AND is_approved = 1", [business_id]
        )
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Business not found")

        business = dict(row)

        cursor = await db.execute(
            "SELECT * FROM deals WHERE business_id = ? AND is_active = 1 ORDER BY created_at DESC",
            [business_id],
        )
        business["deals"] = [dict(r) for r in await cursor.fetchall()]

        cursor = await db.execute(
            "SELECT * FROM reviews WHERE business_id = ? ORDER BY created_at DESC",
            [business_id],
        )
        business["reviews"] = [dict(r) for r in await cursor.fetchall()]

        return {"data": business, "error": None}
    finally:
        await db.close()


@router.post("/")
async def register_business(business: BusinessCreate):
    """Register a new minority-owned business."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO businesses
               (name, description, story, category, address, phone, website, image_url, is_approved)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            [
                business.name,
                business.description,
                business.story,
                business.category,
                business.address,
                business.phone,
                business.website,
                business.image_url,
            ],
        )
        await db.commit()
        new_id = cursor.lastrowid
        cursor = await db.execute("SELECT * FROM businesses WHERE id = ?", [new_id])
        row = await cursor.fetchone()
        return {"data": dict(row), "error": None}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await db.close()
