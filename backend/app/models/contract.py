from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ContractStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"

class Contract(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    contract_number: str = Field(unique=True, index=True)
    quantity_kg: float
    unit_price_ngn: float
    total_amount_ngn: float
    delivery_date: datetime
    delivery_location: str
    terms_and_conditions: Optional[str] = None
    status: ContractStatus = Field(default=ContractStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Foreign keys
    farmer_id: int = Field(foreign_key="user.id")
    buyer_id: int = Field(foreign_key="user.id")
    listing_id: int = Field(foreign_key="listing.id")
    offer_id: int = Field(foreign_key="offer.id")
    
    # Relationships
    offer: "Offer" = Relationship(back_populates="contract")
    escrow: Optional["Escrow"] = Relationship(back_populates="contract")
    orders: List["Order"] = Relationship(back_populates="contract")
    
    class Config:
        arbitrary_types_allowed = True
