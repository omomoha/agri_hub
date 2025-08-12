from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session, select
from app.core.auth import get_current_user, require_admin
from app.core.database import get_session
from app.models.user import User
from app.models.kyc import KYC, KYCStatus, DocumentType
from app.schemas.kyc import KYCCreate, KYCResponse, KYCUpdate
import json
import os
from datetime import datetime
from app.core.config import settings

router = APIRouter()

@router.post("/upload", response_model=KYCResponse)
async def upload_kyc_documents(
    document_type: DocumentType,
    document_number: str,
    document_file: UploadFile = File(...),
    selfie_file: UploadFile = File(None),
    business_registration: UploadFile = File(None),
    business_address: str = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Check if user already has KYC
    existing_kyc = session.exec(
        select(KYC).where(KYC.user_id == current_user.id)
    ).first()
    
    if existing_kyc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="KYC already submitted"
        )
    
    # Create storage directory if it doesn't exist
    os.makedirs(settings.file_storage_dir, exist_ok=True)
    
    # Save document file
    document_filename = f"kyc_{current_user.id}_{document_type}_{document_file.filename}"
    document_path = os.path.join(settings.file_storage_dir, document_filename)
    
    with open(document_path, "wb") as buffer:
        content = await document_file.read()
        buffer.write(content)
    
    # Save selfie if provided
    selfie_path = None
    if selfie_file:
        selfie_filename = f"kyc_{current_user.id}_selfie_{selfie_file.filename}"
        selfie_path = os.path.join(settings.file_storage_dir, selfie_filename)
        
        with open(selfie_path, "wb") as buffer:
            content = await selfie_file.read()
            buffer.write(content)
    
    # Save business registration if provided
    business_reg_path = None
    if business_registration:
        business_filename = f"kyc_{current_user.id}_business_{business_registration.filename}"
        business_reg_path = os.path.join(settings.file_storage_dir, business_filename)
        
        with open(business_reg_path, "wb") as buffer:
            content = await business_registration.read()
            buffer.write(content)
    
    # Create KYC record
    kyc = KYC(
        user_id=current_user.id,
        document_type=document_type,
        document_number=document_number,
        document_file_path=document_path,
        selfie_file_path=selfie_path,
        business_registration=business_reg_path,
        business_address=business_address,
        status=KYCStatus.PENDING
    )
    
    session.add(kyc)
    session.commit()
    session.refresh(kyc)
    
    return KYCResponse.from_orm(kyc)

@router.get("/status", response_model=KYCResponse)
async def get_kyc_status(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    kyc = session.exec(
        select(KYC).where(KYC.user_id == current_user.id)
    ).first()
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC not found"
        )
    
    return KYCResponse.from_orm(kyc)

@router.get("/admin/queue", response_model=list[KYCResponse])
async def get_kyc_queue(
    admin_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    kyc_list = session.exec(
        select(KYC).where(KYC.status == KYCStatus.PENDING)
    ).all()
    
    return [KYCResponse.from_orm(kyc) for kyc in kyc_list]

@router.put("/admin/{kyc_id}/review", response_model=KYCResponse)
async def review_kyc(
    kyc_id: int,
    status: KYCStatus,
    admin_notes: str = None,
    admin_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    kyc = session.exec(select(KYC).where(KYC.id == kyc_id)).first()
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC not found"
        )
    
    # Update KYC status
    kyc.status = status
    kyc.admin_notes = admin_notes
    kyc.reviewed_by = admin_user.id
    kyc.reviewed_at = datetime.utcnow()
    
    # Update user verification status if approved
    if status == KYCStatus.APPROVED:
        user = session.exec(select(User).where(User.id == kyc.user_id)).first()
        if user:
            user.is_verified = True
            user.kyc_status = "approved"
    
    session.commit()
    session.refresh(kyc)
    
    return KYCResponse.from_orm(kyc)
