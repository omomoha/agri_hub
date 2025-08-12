from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.auth import get_current_user, require_role
from app.core.database import get_session
from app.models.user import User, UserRole
from app.models.farm import Farm
from app.schemas.farm import FarmCreate, FarmResponse, FarmUpdate
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=FarmResponse)
async def create_farm(
    farm_data: FarmCreate,
    current_user: User = Depends(require_role("farmer")),
    session: Session = Depends(get_session)
):
    # Check if user is KYC verified
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="KYC verification required to create farms"
        )
    
    farm = Farm(
        **farm_data.dict(),
        farmer_id=current_user.id
    )
    
    session.add(farm)
    session.commit()
    session.refresh(farm)
    
    return FarmResponse.from_orm(farm)

@router.get("/", response_model=list[FarmResponse])
async def get_farms(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if current_user.role == UserRole.FARMER:
        # Farmers can only see their own farms
        farms = session.exec(
            select(Farm).where(Farm.farmer_id == current_user.id)
        ).all()
    else:
        # Other users can see all active farms
        farms = session.exec(
            select(Farm).where(Farm.is_active == True)
        ).all()
    
    return [FarmResponse.from_orm(farm) for farm in farms]

@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    farm = session.exec(select(Farm).where(Farm.id == farm_id)).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    # Check if user can view this farm
    if current_user.role == UserRole.FARMER and farm.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return FarmResponse.from_orm(farm)

@router.put("/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: int,
    farm_update: FarmUpdate,
    current_user: User = Depends(require_role("farmer")),
    session: Session = Depends(get_session)
):
    farm = session.exec(select(Farm).where(Farm.id == farm_id)).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    # Check if user owns this farm
    if farm.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update farm fields
    for field, value in farm_update.dict(exclude_unset=True).items():
        setattr(farm, field, value)
    
    farm.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(farm)
    
    return FarmResponse.from_orm(farm)
