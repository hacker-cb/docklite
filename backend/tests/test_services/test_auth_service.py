import pytest
from datetime import timedelta
from app.services.auth_service import AuthService
from app.models.schemas import UserCreate


@pytest.mark.asyncio
class TestPasswordHashing:
    """Tests for password hashing functionality"""
    
    async def test_password_hash_creates_hash(self, db_session):
        """Test that password hashing creates a hash"""
        plain_password = "mypassword123"
        
        hashed = AuthService.get_password_hash(plain_password)
        
        assert hashed is not None
        assert hashed != plain_password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt format
    
    async def test_password_verify_correct(self, db_session):
        """Test that correct password is verified"""
        plain_password = "mypassword123"
        hashed = AuthService.get_password_hash(plain_password)
        
        is_valid = AuthService.verify_password(plain_password, hashed)
        
        assert is_valid is True
    
    async def test_password_verify_incorrect(self, db_session):
        """Test that incorrect password is rejected"""
        plain_password = "mypassword123"
        wrong_password = "wrongpassword"
        hashed = AuthService.get_password_hash(plain_password)
        
        is_valid = AuthService.verify_password(wrong_password, hashed)
        
        assert is_valid is False
    
    async def test_same_password_different_hashes(self, db_session):
        """Test that same password creates different hashes (salt)"""
        plain_password = "mypassword123"
        
        hash1 = AuthService.get_password_hash(plain_password)
        hash2 = AuthService.get_password_hash(plain_password)
        
        assert hash1 != hash2
        # But both should verify correctly
        assert AuthService.verify_password(plain_password, hash1)
        assert AuthService.verify_password(plain_password, hash2)


@pytest.mark.asyncio
class TestJWTTokens:
    """Tests for JWT token functionality"""
    
    async def test_create_token(self, db_session):
        """Test that JWT token is created"""
        data = {"sub": "testuser"}
        
        token = AuthService.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    async def test_decode_token(self, db_session):
        """Test that JWT token is decoded correctly"""
        username = "testuser"
        data = {"sub": username}
        
        token = AuthService.create_access_token(data)
        decoded = AuthService.decode_token(token)
        
        assert decoded is not None
        assert decoded.username == username
    
    async def test_decode_invalid_token(self, db_session):
        """Test that invalid token is rejected"""
        invalid_token = "this.is.not.a.valid.token"
        
        decoded = AuthService.decode_token(invalid_token)
        
        assert decoded is None
    
    async def test_token_with_expiration(self, db_session):
        """Test that token can be created with custom expiration"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=30)
        
        token = AuthService.create_access_token(data, expires_delta)
        decoded = AuthService.decode_token(token)
        
        assert decoded is not None
        assert decoded.username == "testuser"


@pytest.mark.asyncio
class TestUserCreation:
    """Tests for user creation functionality"""
    
    async def test_create_user_success(self, db_session):
        """Test successful user creation"""
        service = AuthService(db_session)
        
        user_data = UserCreate(
            username="newuser",
            email="new@example.com",
            password="password123"
        )
        
        user, error = await service.create_user(user_data)
        
        assert error is None
        assert user is not None
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.password_hash != "password123"  # Should be hashed
        assert user.is_active == 1
    
    async def test_create_user_duplicate_username(self, db_session):
        """Test that duplicate username is rejected"""
        service = AuthService(db_session)
        
        user_data = UserCreate(
            username="testuser",
            password="password123"
        )
        
        # Create first user
        await service.create_user(user_data)
        
        # Try to create second with same username
        user2, error = await service.create_user(user_data)
        
        assert user2 is None
        assert error is not None
        assert "already exists" in error.lower()
    
    async def test_authenticate_user_success(self, db_session):
        """Test successful user authentication"""
        service = AuthService(db_session)
        
        # Create user
        await service.create_user(UserCreate(
            username="testuser",
            password="testpass123"
        ))
        
        # Authenticate
        user = await service.authenticate_user("testuser", "testpass123")
        
        assert user is not None
        assert user.username == "testuser"
    
    async def test_authenticate_user_wrong_password(self, db_session):
        """Test authentication with wrong password"""
        service = AuthService(db_session)
        
        # Create user
        await service.create_user(UserCreate(
            username="testuser",
            password="correctpass"
        ))
        
        # Try to authenticate with wrong password
        user = await service.authenticate_user("testuser", "wrongpass")
        
        assert user is None
    
    async def test_authenticate_nonexistent_user(self, db_session):
        """Test authentication of non-existent user"""
        service = AuthService(db_session)
        
        user = await service.authenticate_user("nonexistent", "anypass")
        
        assert user is None
    
    async def test_has_users_empty_db(self, db_session):
        """Test has_users on empty database"""
        service = AuthService(db_session)
        
        has_users = await service.has_users()
        
        assert has_users is False
    
    async def test_has_users_with_users(self, db_session):
        """Test has_users when users exist"""
        service = AuthService(db_session)
        
        # Create user
        await service.create_user(UserCreate(
            username="testuser",
            password="testpass123"
        ))
        
        has_users = await service.has_users()
        
        assert has_users is True

