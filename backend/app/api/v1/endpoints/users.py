from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.auth import get_current_user, require_admin
from app.core.database import get_session
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()

@router.get("/", response_model=list[UserResponse])
async def get_users(
    admin_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    users = session.exec(select(User)).all()
    return [UserResponse.from_orm(user) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Users can only view their own profile or admins can view any
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Users can only update their own profile or admins can update any
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    session.commit()
    session.refresh(user)
    
    return UserResponse.from_orm(user)
