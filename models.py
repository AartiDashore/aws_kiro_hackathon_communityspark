from pydantic import BaseModel
from typing import Optional


class BusinessCreate(BaseModel):
    name: str
    description: str
    story: str
    category: str
    address: str
    phone: Optional[str] = None
    website: Optional[str] = None
    image_url: Optional[str] = None


class DealCreate(BaseModel):
    business_id: int
    title: str
    description: Optional[str] = None
    discount_percent: int
    original_price: Optional[float] = None
    expires_in_hours: float = 24.0


class ReviewCreate(BaseModel):
    business_id: int
    rating: int
    comment: Optional[str] = None
