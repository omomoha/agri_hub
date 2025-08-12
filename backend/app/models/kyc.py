from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    NATIONAL_ID = "national_id"
    DRIVERS_LICENSE = "drivers_license"
    PASSPORT = "passport"
    CAC_CERTIFICATE = "cac_certificate"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    OTHER = "other"

class KYCStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"

class KYC(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    document_type: DocumentType
    document_number: str
    document_file_path: str
    selfie_file_path: Optional[str] = None
    business_registration: Optional[str] = None
    business_address: Optional[str] = None
    status: KYCStatus = Field(default=KYCStatus.PENDING)
    admin_notes: Optional[str] = None
    reviewed_by: Optional[int] = Field(foreign_key="user.id", default=None)
    reviewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
