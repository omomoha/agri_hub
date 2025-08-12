from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_number: str = Field(unique=True, index=True)
    quantity_kg: float
    delivery_address: str
    delivery_instructions: Optional[str] = None
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    confirmed_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Foreign keys
    contract_id: int = Field(foreign_key="contract.id")
    farmer_id: int = Field(foreign_key="user.id")
    buyer_id: int = Field(foreign_key="user.id")
    logistics_id: Optional[int] = Field(foreign_key="user.id", default=None)
    
    # Relationships
    contract: "Contract" = Relationship(back_populates="orders")
    
    class Config:
        arbitrary_types_allowed = True
