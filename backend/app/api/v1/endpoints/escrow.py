from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.auth import get_current_user
from app.core.database import get_session
from app.models.user import User
from app.models.escrow import Escrow, EscrowStatus
from app.models.contract import Contract
from app.schemas.escrow import EscrowResponse
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/{contract_id}/create", response_model=EscrowResponse)
async def create_escrow(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get the contract
    contract = session.exec(select(Contract).where(Contract.id == contract_id)).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # Check if user is the buyer
    if contract.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyers can create escrow"
        )
    
    # Check if escrow already exists
    existing_escrow = session.exec(
        select(Escrow).where(Escrow.contract_id == contract_id)
    ).first()
    
    if existing_escrow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Escrow already exists for this contract"
        )
    
    # Generate escrow number
    escrow_number = f"ESC-{uuid.uuid4().hex[:8].upper()}"
    
    # Create escrow
    escrow = Escrow(
        escrow_number=escrow_number,
        amount_ngn=contract.total_amount_ngn,
        contract_id=contract.id,
        buyer_id=contract.buyer_id,
        seller_id=contract.farmer_id
    )
    
    session.add(escrow)
    session.commit()
    session.refresh(escrow)
    
    return EscrowResponse.from_orm(escrow)

@router.post("/{escrow_id}/fund", response_model=EscrowResponse)
async def fund_escrow(
    escrow_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    escrow = session.exec(select(Escrow).where(Escrow.id == escrow_id)).first()
    if not escrow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escrow not found"
        )
    
    # Check if user is the buyer
    if escrow.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyers can fund escrow"
        )
    
    # Check if escrow is in pending status
    if escrow.status != EscrowStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Escrow is not in pending status"
        )
    
    # Mock PSP integration - in real implementation, this would call payment gateway
    escrow.status = EscrowStatus.FUNDED
    escrow.funded_at = datetime.utcnow()
    
    session.commit()
    session.refresh(escrow)
    
    return EscrowResponse.from_orm(escrow)

@router.get("/", response_model=list[EscrowResponse])
async def get_escrows(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Users can see escrows they're involved in
    escrows = session.exec(
        select(Escrow).where(
            (Escrow.buyer_id == current_user.id) | 
            (Escrow.seller_id == current_user.id)
        )
    ).all()
    
    return [EscrowResponse.from_orm(escrow) for escrow in escrows]

@router.get("/{escrow_id}", response_model=EscrowResponse)
async def get_escrow(
    escrow_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    escrow = session.exec(select(Escrow).where(Escrow.id == escrow_id)).first()
    if not escrow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escrow not found"
        )
    
    # Check if user is involved in this escrow
    if escrow.buyer_id != current_user.id and escrow.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return EscrowResponse.from_orm(escrow)
