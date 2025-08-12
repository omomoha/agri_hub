from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    phone: Optional[str] = None
    role: UserRole
    business_name: Optional[str] = None
    business_address: Optional[str] = None
    business_registration: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    kyc_status: str
    business_name: Optional[str] = None
    business_address: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    business_name: Optional[str] = None
    business_address: Optional[str] = None
    business_registration: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
