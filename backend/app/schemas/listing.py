from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.listing import ProduceType, ListingStatus

class ListingCreate(BaseModel):
    title: str
    description: Optional[str] = None
    produce_type: ProduceType
    quantity_kg: float
    unit_price_ngn: float
    harvest_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_organic: bool = False
    quality_grade: Optional[str] = None
    farm_id: int

class ListingResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    produce_type: ProduceType
    quantity_kg: float
    unit_price_ngn: float
    total_price_ngn: float
    harvest_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    status: ListingStatus
    is_organic: bool
    quality_grade: Optional[str] = None
    farmer_id: int
    farm_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    quantity_kg: Optional[float] = None
    unit_price_ngn: Optional[float] = None
    expiry_date: Optional[datetime] = None
    is_organic: Optional[bool] = None
    quality_grade: Optional[str] = None
    status: Optional[ListingStatus] = None
