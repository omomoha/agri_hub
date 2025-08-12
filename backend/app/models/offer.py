from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from enum import Enum

class OfferStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class Offer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quantity_kg: float
    unit_price_ngn: float
    total_price_ngn: float
    delivery_date: Optional[datetime] = None
    delivery_location: str
    notes: Optional[str] = None
    status: OfferStatus = Field(default=OfferStatus.PENDING)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Foreign keys
    buyer_id: int = Field(foreign_key="user.id")
    listing_id: int = Field(foreign_key="listing.id")
    
    # Relationships
    listing: "Listing" = Relationship(back_populates="offers")
    contract: Optional["Contract"] = Relationship(back_populates="offer")
    
    class Config:
        arbitrary_types_allowed = True
