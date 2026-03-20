"""
Implementing businesses router with CRUD endpoints
Author: Aarti Dashore
Version: 1.0.0
"""

import os
import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File
from models import BusinessCreate, BusinessUpdate
from database import get_db

router = APIRouter()

UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "static", "uploads"
)
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB


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


@router.delete("/{business_id}/image")
async def delete_image(business_id: int):
    """Remove the photo from a business listing and delete the file from disk."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT image_url FROM businesses WHERE id = ?", [business_id]
        )
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Business not found")
        image_url = row["image_url"]
        if image_url and image_url.startswith("/static/uploads/"):
            filepath = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), image_url.lstrip("/")
            )
            if os.path.isfile(filepath):
                os.remove(filepath)
        await db.execute(
            "UPDATE businesses SET image_url = NULL WHERE id = ?", [business_id]
        )
        await db.commit()
        return {"data": {"success": True}, "error": None}
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


@router.put("/{business_id}")
async def update_business(business_id: int, updates: BusinessUpdate):
    """Update fields on an existing business."""
    fields = {k: v for k, v in updates.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided to update")
    db = await get_db()
    try:
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        await db.execute(
            f"UPDATE businesses SET {set_clause} WHERE id = ?",
            [*fields.values(), business_id],
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT * FROM businesses WHERE id = ?", [business_id]
        )
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Business not found")
        return {"data": dict(row), "error": None}
    finally:
        await db.close()


@router.delete("/{business_id}")
async def delete_business(business_id: int):
    """Delete a business and all its associated deals and reviews."""
    db = await get_db()
    try:
        await db.execute("DELETE FROM reviews WHERE business_id = ?", [business_id])
        await db.execute("DELETE FROM deals WHERE business_id = ?", [business_id])
        await db.execute("DELETE FROM businesses WHERE id = ?", [business_id])
        await db.commit()
        return {"data": {"success": True}, "error": None}
    finally:
        await db.close()


@router.post("/{business_id}/image")
async def upload_image(business_id: int, file: UploadFile = File(...)):
    """Upload a photo for a business listing."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400, detail="Only JPEG, PNG, WebP, or GIF images are allowed"
        )
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Image must be under 5 MB")
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"{business_id}_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(contents)
    image_url = f"/static/uploads/{filename}"
    db = await get_db()
    try:
        await db.execute(
            "UPDATE businesses SET image_url = ? WHERE id = ?", [image_url, business_id]
        )
        await db.commit()
        return {"data": {"image_url": image_url}, "error": None}
    finally:
        await db.close()
