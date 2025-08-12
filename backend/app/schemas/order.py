from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.order import OrderStatus

class OrderResponse(BaseModel):
    id: int
    order_number: str
    quantity_kg: float
    delivery_address: str
    delivery_instructions: Optional[str] = None
    status: OrderStatus
    confirmed_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    contract_id: int
    farmer_id: int
    buyer_id: int
    logistics_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
