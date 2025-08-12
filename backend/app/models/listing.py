from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ProduceType(str, Enum):
    GRAINS = "grains"
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    TUBERS = "tubers"
    LEGUMES = "legumes"
    OTHER = "other"

class ListingStatus(str, Enum):
    ACTIVE = "active"
    SOLD = "sold"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class Listing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    produce_type: ProduceType
    quantity_kg: float
    unit_price_ngn: float
    total_price_ngn: float
    harvest_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    status: ListingStatus = Field(default=ListingStatus.ACTIVE)
    is_organic: bool = Field(default=False)
    quality_grade: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Foreign keys
    farmer_id: int = Field(foreign_key="user.id")
    farm_id: int = Field(foreign_key="farm.id")
    
    # Relationships
    farm: "Farm" = Relationship(back_populates="listings")
    offers: List["Offer"] = Relationship(back_populates="listing")
    
    class Config:
        arbitrary_types_allowed = True
