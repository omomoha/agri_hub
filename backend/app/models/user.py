from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    FARMER = "farmer"
    AGGREGATOR = "aggregator"
    BUYER = "buyer"
    LOGISTICS = "logistics"
    ADMIN = "admin"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # KYC verification
    kyc_status: str = Field(default="pending")  # pending, approved, rejected
    kyc_documents: Optional[str] = None  # JSON string of document paths
    
    # Business details
    business_name: Optional[str] = None
    business_address: Optional[str] = None
    business_registration: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True
