from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.contract import ContractStatus

class ContractResponse(BaseModel):
    id: int
    contract_number: str
    quantity_kg: float
    unit_price_ngn: float
    total_amount_ngn: float
    delivery_date: datetime
    delivery_location: str
    terms_and_conditions: Optional[str] = None
    status: ContractStatus
    farmer_id: int
    buyer_id: int
    listing_id: int
    offer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
