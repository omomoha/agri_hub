from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from enum import Enum

class EscrowStatus(str, Enum):
    PENDING = "pending"
    FUNDED = "funded"
    RELEASED = "released"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

class Escrow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    escrow_number: str = Field(unique=True, index=True)
    amount_ngn: float
    status: EscrowStatus = Field(default=EscrowStatus.PENDING)
    funded_at: Optional[datetime] = None
    released_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Foreign keys
    contract_id: int = Field(foreign_key="contract.id")
    buyer_id: int = Field(foreign_key="user.id")
    seller_id: int = Field(foreign_key="user.id")
    
    # Relationships
    contract: "Contract" = Relationship(back_populates="escrow")
    
    class Config:
        arbitrary_types_allowed = True
