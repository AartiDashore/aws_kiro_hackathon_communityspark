"""
Implementing reviews router with CRUD endpoints
Author: Aarti Dashore
Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException
from models import ReviewCreate
from database import get_db

router = APIRouter()


@router.post("/")
async def submit_review(review: ReviewCreate):
    """Submit a star rating and review for a business."""
    if not (1 <= review.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    db = await get_db()
    try:
        cursor = await db.execute(
            "INSERT INTO reviews (business_id, rating, comment) VALUES (?, ?, ?)",
            [review.business_id, review.rating, review.comment],
        )
        await db.commit()
        new_id = cursor.lastrowid
        cursor = await db.execute("SELECT * FROM reviews WHERE id = ?", [new_id])
        row = await cursor.fetchone()
        return {"data": dict(row), "error": None}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await db.close()


@router.get("/{business_id}")
async def get_reviews(business_id: int):
    """Get all reviews for a specific business."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM reviews WHERE business_id = ? ORDER BY created_at DESC",
            [business_id],
        )
        rows = await cursor.fetchall()
        return {"data": [dict(r) for r in rows], "error": None}
    finally:
        await db.close()
