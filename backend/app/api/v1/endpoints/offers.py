from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.auth import get_current_user, require_role
from app.core.database import get_session
from app.models.user import User, UserRole
from app.models.offer import Offer, OfferStatus
from app.models.listing import Listing, ListingStatus
from app.schemas.offer import OfferCreate, OfferResponse
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/", response_model=OfferResponse)
async def create_offer(
    offer_data: OfferCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Check if user is not a farmer (buyers/aggregators make offers)
    if current_user.role == UserRole.FARMER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Farmers cannot make offers"
        )
    
    # Verify listing exists and is active
    listing = session.exec(select(Listing).where(Listing.id == offer_data.listing_id)).first()
    if not listing or listing.status != ListingStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or inactive listing"
        )
    
    # Check if user is not offering on their own listing
    if listing.farmer_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot make offer on your own listing"
        )
    
    # Calculate total price
    total_price = offer_data.quantity_kg * offer_data.unit_price_ngn
    
    # Set expiration (7 days from now)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    offer = Offer(
        **offer_data.dict(),
        buyer_id=current_user.id,
        total_price_ngn=total_price,
        expires_at=expires_at
    )
    
    session.add(offer)
    session.commit()
    session.refresh(offer)
    
    return OfferResponse.from_orm(offer)

@router.get("/", response_model=list[OfferResponse])
async def get_offers(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if current_user.role == UserRole.FARMER:
        # Farmers see offers on their listings
        listings = session.exec(select(Listing).where(Listing.farmer_id == current_user.id)).all()
        listing_ids = [listing.id for listing in listings]
        offers = session.exec(select(Offer).where(Offer.listing_id.in_(listing_ids))).all()
    else:
        # Buyers see their own offers
        offers = session.exec(select(Offer).where(Offer.buyer_id == current_user.id)).all()
    
    return [OfferResponse.from_orm(offer) for offer in offers]

@router.post("/{offer_id}/accept", response_model=dict)
async def accept_offer(
    offer_id: int,
    current_user: User = Depends(require_role("farmer")),
    session: Session = Depends(get_session)
):
    offer = session.exec(select(Offer).where(Offer.id == offer_id)).first()
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found"
        )
    
    # Verify listing ownership
    listing = session.exec(select(Listing).where(Listing.id == offer.listing_id)).first()
    if not listing or listing.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if offer is still valid
    if offer.status != OfferStatus.PENDING or offer.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offer is no longer valid"
        )
    
    # Accept the offer
    offer.status = OfferStatus.ACCEPTED
    session.commit()
    
    return {"message": "Offer accepted successfully"}
