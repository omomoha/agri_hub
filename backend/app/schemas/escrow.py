from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.escrow import EscrowStatus

class EscrowResponse(BaseModel):
    id: int
    escrow_number: str
    amount_ngn: float
    status: EscrowStatus
    funded_at: Optional[datetime] = None
    released_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    contract_id: int
    buyer_id: int
    seller_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
