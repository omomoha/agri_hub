from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.auth import get_current_user
from app.core.database import get_session
from app.models.user import User
from app.models.contract import Contract
from app.models.offer import Offer, OfferStatus
from app.models.listing import Listing, ListingStatus
from app.schemas.contract import ContractResponse
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/{offer_id}/create", response_model=ContractResponse)
async def create_contract(
    offer_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get the accepted offer
    offer = session.exec(select(Offer).where(Offer.id == offer_id)).first()
    if not offer or offer.status != OfferStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unaccepted offer"
        )
    
    # Verify user is the farmer who accepted the offer
    listing = session.exec(select(Listing).where(Listing.id == offer.listing_id)).first()
    if not listing or listing.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Generate contract number
    contract_number = f"CTR-{uuid.uuid4().hex[:8].upper()}"
    
    # Create contract
    contract = Contract(
        contract_number=contract_number,
        quantity_kg=offer.quantity_kg,
        unit_price_ngn=offer.unit_price_ngn,
        total_amount_ngn=offer.total_price_ngn,
        delivery_date=offer.delivery_date or datetime.utcnow(),
        delivery_location=offer.delivery_location,
        farmer_id=listing.farmer_id,
        buyer_id=offer.buyer_id,
        listing_id=offer.listing_id,
        offer_id=offer.id
    )
    
    # Update listing status to sold
    listing.status = ListingStatus.SOLD
    
    session.add(contract)
    session.commit()
    session.refresh(contract)
    
    return ContractResponse.from_orm(contract)

@router.get("/", response_model=list[ContractResponse])
async def get_contracts(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Users can see contracts they're involved in
    contracts = session.exec(
        select(Contract).where(
            (Contract.farmer_id == current_user.id) | 
            (Contract.buyer_id == current_user.id)
        )
    ).all()
    
    return [ContractResponse.from_orm(contract) for contract in contracts]

@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    contract = session.exec(select(Contract).where(Contract.id == contract_id)).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # Check if user is involved in this contract
    if contract.farmer_id != current_user.id and contract.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return ContractResponse.from_orm(contract)
