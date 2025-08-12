from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.offer import OfferStatus

class OfferCreate(BaseModel):
    quantity_kg: float
    unit_price_ngn: float
    delivery_date: Optional[datetime] = None
    delivery_location: str
    notes: Optional[str] = None
    listing_id: int

class OfferResponse(BaseModel):
    id: int
    quantity_kg: float
    unit_price_ngn: float
    total_price_ngn: float
    delivery_date: Optional[datetime] = None
    delivery_location: str
    notes: Optional[str] = None
    status: OfferStatus
    expires_at: datetime
    buyer_id: int
    listing_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OfferUpdate(BaseModel):
    quantity_kg: Optional[float] = None
    unit_price_ngn: Optional[float] = None
    delivery_date: Optional[datetime] = None
    delivery_location: Optional[str] = None
    notes: Optional[str] = None
