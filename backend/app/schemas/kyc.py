from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.kyc import DocumentType, KYCStatus

class KYCCreate(BaseModel):
    document_type: DocumentType
    document_number: str
    business_address: Optional[str] = None

class KYCResponse(BaseModel):
    id: int
    user_id: int
    document_type: DocumentType
    document_number: str
    document_file_path: str
    selfie_file_path: Optional[str] = None
    business_registration: Optional[str] = None
    business_address: Optional[str] = None
    status: KYCStatus
    admin_notes: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class KYCUpdate(BaseModel):
    status: KYCStatus
    admin_notes: Optional[str] = None
