import pytest
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, UserUpdate
from app.core.auth import get_password_hash, verify_password
from sqlmodel import Session, select
from datetime import datetime

class TestUserModel:
    """Test User model functionality."""
    
    def test_user_creation(self, session):
        """Test creating a new user."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "hashed_password": get_password_hash("password123"),
            "full_name": "New User",
            "phone": "+1234567890",
            "role": UserRole.FARMER,
            "is_active": True,
            "is_verified": False,
            "kyc_status": "pending"
        }
        
        user = User(**user_data)
        session.add(user)
        session.commit()
        session.refresh(user)
        
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.username == "newuser"
        assert user.full_name == "New User"
        assert user.role == UserRole.FARMER
        assert user.is_active is True
        assert user.is_verified is False
        assert user.kyc_status == "pending"
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_password_verification(self, session):
        """Test user password verification."""
        password = "securepassword123"
        hashed = get_password_hash(password)
        
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=hashed,
            full_name="Test User",
            phone="+1234567890",
            role=UserRole.FARMER
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        assert verify_password(password, user.hashed_password) is True
        assert verify_password("wrongpassword", user.hashed_password) is False
    
    def test_user_role_enum(self, session):
        """Test user role enumeration values."""
        roles = [UserRole.FARMER, UserRole.BUYER, UserRole.AGGREGATOR, UserRole.LOGISTICS, UserRole.ADMIN]
        
        for i, role in enumerate(roles):
            user = User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                hashed_password=get_password_hash("password123"),
                full_name=f"User {i}",
                phone="+1234567890",
                role=role
            )
            session.add(user)
        
        session.commit()
        
        # Verify all roles were saved correctly
        for i, role in enumerate(roles):
            user = session.exec(select(User).where(User.email == f"user{i}@example.com")).first()
            assert user.role == role
    
    def test_user_timestamps(self, session):
        """Test that user timestamps are set correctly."""
        before_creation = datetime.now()
        
        user = User(
            email="timestamp@example.com",
            username="timestamp",
            hashed_password=get_password_hash("password123"),
            full_name="Timestamp User",
            phone="+1234567890",
            role=UserRole.FARMER
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        after_creation = datetime.now()
        
        assert user.created_at >= before_creation
        assert user.created_at <= after_creation
        assert user.updated_at >= before_creation
        assert user.updated_at <= after_creation
        assert user.created_at == user.updated_at  # Initially they should be the same

class TestUserSchemas:
    """Test user Pydantic schemas."""
    
    def test_user_create_schema(self):
        """Test UserCreate schema validation."""
        user_data = {
            "email": "schema@example.com",
            "username": "schemauser",
            "password": "password123",
            "full_name": "Schema User",
            "phone": "+1234567890",
            "role": "farmer",
            "business_name": "Test Business",
            "business_address": "Test Address"
        }
        
        user_create = UserCreate(**user_data)
        
        assert user_create.email == "schema@example.com"
        assert user_create.username == "schemauser"
        assert user_create.password == "password123"
        assert user_create.full_name == "Schema User"
        assert user_create.phone == "+1234567890"
        assert user_create.role == "farmer"
        assert user_create.business_name == "Test Business"
        assert user_create.business_address == "Test Address"
    
    def test_user_login_schema(self):
        """Test UserLogin schema validation."""
        login_data = {
            "email": "login@example.com",
            "password": "password123"
        }
        
        user_login = UserLogin(**login_data)
        
        assert user_login.email == "login@example.com"
        assert user_login.password == "password123"
    
    def test_user_update_schema(self):
        """Test UserUpdate schema validation."""
        update_data = {
            "full_name": "Updated Name",
            "phone": "+9876543210",
            "business_name": "Updated Business"
        }
        
        user_update = UserUpdate(**update_data)
        
        assert user_update.full_name == "Updated Name"
        assert user_update.phone == "+9876543210"
        assert user_update.business_name == "Updated Business"
        assert user_update.email is None  # Not provided, should be None

class TestUserValidation:
    """Test user data validation."""
    
    def test_email_validation(self):
        """Test email format validation."""
        # Valid email
        valid_data = {
            "email": "valid@example.com",
            "username": "validuser",
            "password": "password123",
            "full_name": "Valid User",
            "phone": "+1234567890",
            "role": "farmer"
        }
        user_create = UserCreate(**valid_data)
        assert user_create.email == "valid@example.com"
        
        # Invalid email should raise validation error
        with pytest.raises(ValueError):
            invalid_data = valid_data.copy()
            invalid_data["email"] = "invalid-email"
            UserCreate(**invalid_data)
    
    def test_phone_validation(self):
        """Test phone number validation."""
        # Valid phone numbers
        valid_phones = ["+1234567890", "+2348012345678", "+447911123456"]
        
        for phone in valid_phones:
            data = {
                "email": "phone@example.com",
                "username": "phoneuser",
                "password": "password123",
                "full_name": "Phone User",
                "phone": phone,
                "role": "farmer"
            }
            user_create = UserCreate(**data)
            assert user_create.phone == phone
    
    def test_username_validation(self):
        """Test username validation."""
        # Valid username
        valid_data = {
            "email": "username@example.com",
            "username": "valid_username123",
            "password": "password123",
            "full_name": "Username User",
            "phone": "+1234567890",
            "role": "farmer"
        }
        user_create = UserCreate(**valid_data)
        assert user_create.username == "valid_username123"
        
        # Username with spaces should raise validation error
        with pytest.raises(ValueError):
            invalid_data = valid_data.copy()
            invalid_data["username"] = "invalid username"
            UserCreate(**invalid_data)

class TestUserBusinessLogic:
    """Test user business logic and constraints."""
    
    def test_user_verification_flow(self, session):
        """Test user verification status flow."""
        user = User(
            email="verification@example.com",
            username="verification",
            hashed_password=get_password_hash("password123"),
            full_name="Verification User",
            phone="+1234567890",
            role=UserRole.FARMER,
            is_verified=False,
            kyc_status="pending"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Initially not verified
        assert user.is_verified is False
        assert user.kyc_status == "pending"
        
        # Update KYC status to approved
        user.kyc_status = "approved"
        user.is_verified = True
        session.commit()
        session.refresh(user)
        
        assert user.is_verified is True
        assert user.kyc_status == "approved"
    
    def test_user_deactivation(self, session):
        """Test user deactivation."""
        user = User(
            email="deactivation@example.com",
            username="deactivation",
            hashed_password=get_password_hash("password123"),
            full_name="Deactivation User",
            phone="+1234567890",
            role=UserRole.FARMER,
            is_active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Initially active
        assert user.is_active is True
        
        # Deactivate user
        user.is_active = False
        session.commit()
        session.refresh(user)
        
        assert user.is_active is False
    
    def test_user_role_constraints(self, session):
        """Test user role constraints and business rules."""
        # Test that admin users can be created
        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("password123"),
            full_name="Admin User",
            phone="+1234567890",
            role=UserRole.ADMIN
        )
        session.add(admin)
        session.commit()
        session.refresh(admin)
        
        assert admin.role == UserRole.ADMIN
        
        # Test that logistics users can be created
        logistics = User(
            email="logistics@example.com",
            username="logistics",
            hashed_password=get_password_hash("password123"),
            full_name="Logistics User",
            phone="+1234567890",
            role=UserRole.LOGISTICS
        )
        session.add(logistics)
        session.commit()
        session.refresh(logistics)
        
        assert logistics.role == UserRole.LOGISTICS
