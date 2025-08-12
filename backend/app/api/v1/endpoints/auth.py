from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlmodel import Session, select
from app.core.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.core.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, session: Session = Depends(get_session)):
    # Check if user already exists
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role,
        business_name=user_data.business_name,
        business_address=user_data.business_address,
        business_registration=user_data.business_registration
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return Token(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.from_orm(db_user)
    )

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, session: Session = Depends(get_session)):
    # Find user by email
    user = session.exec(
        select(User).where(User.email == user_credentials.email)
    ).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.from_orm(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)


