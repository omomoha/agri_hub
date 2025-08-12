import pytest
from app.core.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    get_current_user,
    require_role,
    require_admin
)
from app.models.user import User, UserRole
from fastapi import HTTPException, Depends
from sqlmodel import Session

class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_password_hashing_and_verification(self):
        """Test that password hashing and verification work correctly."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Verify the password matches
        assert verify_password(password, hashed) is True
        
        # Verify wrong password doesn't match
        assert verify_password("wrongpassword", hashed) is False
        
        # Verify empty password doesn't match
        assert verify_password("", hashed) is False

class TestJWTTokenCreation:
    """Test JWT token creation and validation."""
    
    def test_create_access_token(self):
        """Test that access tokens are created correctly."""
        data = {"sub": "123"}
        token = create_access_token(data=data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Token should be in format: header.payload.signature
        parts = token.split('.')
        assert len(parts) == 3

class TestUserAuthentication:
    """Test user authentication and authorization."""
    
    def test_get_current_user_valid_token(self, session, test_user):
        """Test getting current user with valid token."""
        token = create_access_token(data={"sub": str(test_user.id)})
        user = get_current_user(token, session)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
        assert user.username == test_user.username
    
    def test_get_current_user_invalid_token(self, session):
        """Test getting current user with invalid token."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user("invalid_token", session)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
    
    def test_get_current_user_expired_token(self, session, test_user):
        """Test getting current user with expired token."""
        # Create a token that expires immediately
        token = create_access_token(data={"sub": str(test_user.id)}, expires_delta=0)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token, session)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
    
    def test_get_current_user_nonexistent_user(self, session):
        """Test getting current user with token for non-existent user."""
        token = create_access_token(data={"sub": "999"})
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token, session)
        
        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)

class TestRoleBasedAccess:
    """Test role-based access control."""
    
    def test_require_role_farmer_success(self, session, test_user):
        """Test that farmer role requirement works for farmer user."""
        token = create_access_token(data={"sub": str(test_user.id)})
        user = get_current_user(token, session)
        
        # This should not raise an exception
        result = require_role("farmer")(user)
        assert result == user
    
    def test_require_role_farmer_failure(self, session, test_buyer):
        """Test that farmer role requirement fails for non-farmer user."""
        token = create_access_token(data={"sub": str(test_buyer.id)})
        user = get_current_user(token, session)
        
        with pytest.raises(HTTPException) as exc_info:
            require_role("farmer")(user)
        
        assert exc_info.value.status_code == 403
        assert "Not enough permissions" in str(exc_info.value.detail)
    
    def test_require_admin_success(self, session, test_admin):
        """Test that admin requirement works for admin user."""
        token = create_access_token(data={"sub": str(test_admin.id)})
        user = get_current_user(token, session)
        
        # This should not raise an exception
        result = require_admin(user)
        assert result == user
    
    def test_require_admin_failure(self, session, test_user):
        """Test that admin requirement fails for non-admin user."""
        token = create_access_token(data={"sub": str(test_user.id)})
        user = get_current_user(token, session)
        
        with pytest.raises(HTTPException) as exc_info:
            require_admin(user)
        
        assert exc_info.value.status_code == 403
        assert "Admin access required" in str(exc_info.value.detail)

class TestAuthenticationEdgeCases:
    """Test authentication edge cases and error handling."""
    
    def test_empty_token(self, session):
        """Test handling of empty token."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user("", session)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
    
    def test_none_token(self, session):
        """Test handling of None token."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(None, session)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
    
    def test_malformed_token(self, session):
        """Test handling of malformed token."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user("not.a.valid.token", session)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
