"""
Implementing Pydantic data models for business, deals, and reviews
Author: Aarti Dashore
Version: 1.0.0
"""

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
    urgency_threshold_hours: Optional[float] = None  # show banner when X hours remain


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    story: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    image_url: Optional[str] = None


class DealUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    discount_percent: Optional[int] = None
    original_price: Optional[float] = None
    extend_hours: Optional[float] = None             # positive = extend, negative = shorten
    urgency_threshold_hours: Optional[float] = None  # update the urgency banner threshold


class ReviewCreate(BaseModel):
    business_id: int
    rating: int
    comment: Optional[str] = None
