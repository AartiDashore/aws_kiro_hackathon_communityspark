from fastapi import APIRouter, HTTPException, BackgroundTasks
from models import DealCreate
from database import get_db
from datetime import datetime, timedelta, timezone
import asyncio

router = APIRouter()


async def expire_deal_after_delay(deal_id: int, seconds: float):
    """Background task: deactivate a deal after its expiry time."""
    await asyncio.sleep(max(seconds, 0))
    db = await get_db()
    try:
        await db.execute("UPDATE deals SET is_active = 0 WHERE id = ?", [deal_id])
        await db.commit()
        print(f"[Hook] Deal {deal_id} auto-expired.")
    finally:
        await db.close()


@router.get("/")
async def list_deals(business_id: int = None):
    """Return all active, non-expired deals with business info."""
    db = await get_db()
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        query = """
            SELECT d.*, b.name AS business_name, b.category AS business_category
            FROM deals d
            JOIN businesses b ON b.id = d.business_id
            WHERE d.is_active = 1 AND d.expires_at > ?
        """
        params = [now]
        if business_id:
            query += " AND d.business_id = ?"
            params.append(business_id)
        query += " ORDER BY d.created_at DESC"
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return {"data": [dict(r) for r in rows], "error": None}
    finally:
        await db.close()


@router.post("/")
async def create_deal(deal: DealCreate, background_tasks: BackgroundTasks):
    """Create a new flash deal and schedule automatic expiry."""
    expires_at = datetime.now(timezone.utc) + timedelta(hours=deal.expires_in_hours)
    expires_str = expires_at.strftime("%Y-%m-%d %H:%M:%S")

    deal_price = None
    if deal.original_price and deal.discount_percent:
        deal_price = round(deal.original_price * (1 - deal.discount_percent / 100), 2)

    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO deals
               (business_id, title, description, discount_percent,
                original_price, deal_price, expires_at, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
            [
                deal.business_id,
                deal.title,
                deal.description,
                deal.discount_percent,
                deal.original_price,
                deal_price,
                expires_str,
            ],
        )
        await db.commit()
        new_id = cursor.lastrowid
        cursor = await db.execute("SELECT * FROM deals WHERE id = ?", [new_id])
        row = dict(await cursor.fetchone())

        delay = deal.expires_in_hours * 3600
        background_tasks.add_task(expire_deal_after_delay, new_id, delay)

        return {"data": row, "error": None}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await db.close()


@router.delete("/{deal_id}")
async def expire_deal(deal_id: int):
    """Manually expire a deal."""
    db = await get_db()
    try:
        await db.execute("UPDATE deals SET is_active = 0 WHERE id = ?", [deal_id])
        await db.commit()
        return {"data": {"success": True}, "error": None}
    finally:
        await db.close()
