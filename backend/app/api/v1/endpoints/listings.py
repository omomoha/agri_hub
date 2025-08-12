from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.auth import get_current_user, require_role
from app.core.database import get_session
from app.models.user import User, UserRole
from app.models.listing import Listing, ListingStatus
from app.models.farm import Farm
from app.schemas.listing import ListingCreate, ListingResponse, ListingUpdate
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=ListingResponse)
async def create_listing(
    listing_data: ListingCreate,
    current_user: User = Depends(require_role("farmer")),
    session: Session = Depends(get_session)
):
    # Check if user is KYC verified
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="KYC verification required to create listings"
        )
    
    # Verify farm ownership
    farm = session.exec(select(Farm).where(Farm.id == listing_data.farm_id)).first()
    if not farm or farm.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid farm or farm ownership"
        )
    
    # Calculate total price
    total_price = listing_data.quantity_kg * listing_data.unit_price_ngn
    
    listing = Listing(
        **listing_data.dict(),
        farmer_id=current_user.id,
        total_price_ngn=total_price
    )
    
    session.add(listing)
    session.commit()
    session.refresh(listing)
    
    return ListingResponse.from_orm(listing)

@router.get("/", response_model=list[ListingResponse])
async def get_listings(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if current_user.role == UserRole.FARMER:
        # Farmers can see their own listings
        listings = session.exec(
            select(Listing).where(Listing.farmer_id == current_user.id)
        ).all()
    else:
        # Other users can see active listings
        listings = session.exec(
            select(Listing).where(Listing.status == ListingStatus.ACTIVE)
        ).all()
    
    return [ListingResponse.from_orm(listing) for listing in listings]

@router.get("", response_model=list[ListingResponse])
async def get_listings_no_slash(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Redirect to the version with trailing slash
    return await get_listings(current_user, session)

@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    listing = session.exec(select(Listing).where(Listing.id == listing_id)).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    return ListingResponse.from_orm(listing)

@router.put("/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: int,
    listing_update: ListingUpdate,
    current_user: User = Depends(require_role("farmer")),
    session: Session = Depends(get_session)
):
    listing = session.exec(select(Listing).where(Listing.id == listing_id)).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    # Check if user owns this listing
    if listing.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update listing fields
    for field, value in listing_update.dict(exclude_unset=True).items():
        setattr(listing, field, value)
    
    # Recalculate total price if quantity or unit price changed
    if listing_update.quantity_kg is not None or listing_update.unit_price_ngn is not None:
        listing.total_price_ngn = listing.quantity_kg * listing.unit_price_ngn
    
    listing.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(listing)
    
    return ListingResponse.from_orm(listing)
