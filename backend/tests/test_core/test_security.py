"""Tests for core security module."""

import pytest
from fastapi import HTTPException
from unittest.mock import Mock, AsyncMock, patch
from app.core.security import (
    get_current_user,
    get_current_active_user,
    get_current_user_with_cookie
)
from app.models.user import User
from app.services.auth_service import AuthService


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, db_session):
        """Test getting current user with valid token."""
        # Create user
        auth_service = AuthService(db_session)
        password_hash = auth_service.get_password_hash("testpass")
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=password_hash,
            is_active=1,
            is_admin=0
        )
        db_session.add(user)
        await db_session.commit()
        
        # Create token
        token = auth_service.create_access_token(data={"sub": "testuser"})
        
        # Mock credentials
        mock_credentials = Mock()
        mock_credentials.credentials = token
        
        # Get user
        result_user = await get_current_user(mock_credentials, db_session)
        
        assert result_user is not None
        assert result_user.username == "testuser"
        assert result_user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, db_session):
        """Test that invalid token raises 401."""
        mock_credentials = Mock()
        mock_credentials.credentials = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, db_session)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_nonexistent_user(self, db_session):
        """Test that token for non-existent user raises 401."""
        # Create token for non-existent user
        auth_service = AuthService(db_session)
        token = auth_service.create_access_token(data={"sub": "nonexistent"})
        
        mock_credentials = Mock()
        mock_credentials.credentials = token
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, db_session)
        
        assert exc_info.value.status_code == 401
        assert "User not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_inactive(self, db_session):
        """Test that inactive user raises 403."""
        # Create inactive user
        auth_service = AuthService(db_session)
        password_hash = auth_service.get_password_hash("testpass")
        user = User(
            username="inactiveuser",
            email="inactive@example.com",
            password_hash=password_hash,
            is_active=0,  # Inactive!
            is_admin=0
        )
        db_session.add(user)
        await db_session.commit()
        
        # Create token
        token = auth_service.create_access_token(data={"sub": "inactiveuser"})
        
        mock_credentials = Mock()
        mock_credentials.credentials = token
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, db_session)
        
        assert exc_info.value.status_code == 403
        assert "Inactive user" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_empty_token(self, db_session):
        """Test that empty token is rejected."""
        mock_credentials = Mock()
        mock_credentials.credentials = ""
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, db_session)
        
        assert exc_info.value.status_code == 401


class TestGetCurrentActiveUser:
    """Tests for get_current_active_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_active_user(self):
        """Test that get_current_active_user passes through user."""
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.is_active = 1
        
        result = await get_current_active_user(mock_user)
        
        assert result == mock_user


class TestGetCurrentUserWithCookie:
    """Tests for get_current_user_with_cookie dependency (Traefik ForwardAuth)."""

    @pytest.mark.asyncio
    async def test_get_user_with_bearer_token(self, db_session):
        """Test priority 1: Authorization header (Bearer token)."""
        # Create user
        auth_service = AuthService(db_session)
        password_hash = auth_service.get_password_hash("testpass")
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=password_hash,
            is_active=1,
            is_admin=1
        )
        db_session.add(user)
        await db_session.commit()
        
        # Create token
        token = auth_service.create_access_token(data={"sub": "testuser"})
        
        # Mock request and credentials
        mock_request = Mock()
        mock_request.cookies = {}  # No cookie
        
        mock_credentials = Mock()
        mock_credentials.credentials = token
        
        # Get user - should use Bearer token (priority 1)
        result_user = await get_current_user_with_cookie(
            mock_request, mock_credentials, db_session
        )
        
        assert result_user is not None
        assert result_user.username == "testuser"

    @pytest.mark.asyncio
    async def test_get_user_with_cookie(self, db_session):
        """Test priority 2: Cookie token."""
        # Create user
        auth_service = AuthService(db_session)
        password_hash = auth_service.get_password_hash("testpass")
        user = User(
            username="cookieuser",
            email="cookie@example.com",
            password_hash=password_hash,
            is_active=1,
            is_admin=1
        )
        db_session.add(user)
        await db_session.commit()
        
        # Create token
        token = auth_service.create_access_token(data={"sub": "cookieuser"})
        
        # Mock request with cookie
        mock_request = Mock()
        mock_request.cookies = {"token": token}
        
        # No Bearer credentials (None)
        mock_credentials = None
        
        # Get user - should use cookie (priority 2)
        result_user = await get_current_user_with_cookie(
            mock_request, mock_credentials, db_session
        )
        
        assert result_user is not None
        assert result_user.username == "cookieuser"

    @pytest.mark.asyncio
    async def test_get_user_bearer_takes_priority_over_cookie(self, db_session):
        """Test that Bearer token has priority over cookie."""
        # Create two users
        auth_service = AuthService(db_session)
        
        # User 1 - for Bearer token
        user1 = User(
            username="beareruser",
            email="bearer@example.com",
            password_hash=auth_service.get_password_hash("pass1"),
            is_active=1,
            is_admin=1
        )
        db_session.add(user1)
        
        # User 2 - for cookie token
        user2 = User(
            username="cookieuser",
            email="cookie@example.com",
            password_hash=auth_service.get_password_hash("pass2"),
            is_active=1,
            is_admin=1
        )
        db_session.add(user2)
        await db_session.commit()
        
        # Create tokens
        bearer_token = auth_service.create_access_token(data={"sub": "beareruser"})
        cookie_token = auth_service.create_access_token(data={"sub": "cookieuser"})
        
        # Mock request with cookie
        mock_request = Mock()
        mock_request.cookies = {"token": cookie_token}
        
        # Mock Bearer credentials
        mock_credentials = Mock()
        mock_credentials.credentials = bearer_token
        
        # Get user - should use Bearer token (priority 1)
        result_user = await get_current_user_with_cookie(
            mock_request, mock_credentials, db_session
        )
        
        assert result_user.username == "beareruser"  # Not cookieuser!

    @pytest.mark.asyncio
    async def test_get_user_no_token_no_cookie(self, db_session):
        """Test that missing token and cookie raises 401."""
        mock_request = Mock()
        mock_request.cookies = {}
        
        mock_credentials = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_with_cookie(
                mock_request, mock_credentials, db_session
            )
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_user_invalid_cookie_token(self, db_session):
        """Test that invalid cookie token raises 401."""
        mock_request = Mock()
        mock_request.cookies = {"token": "invalid.token.here"}
        
        mock_credentials = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_with_cookie(
                mock_request, mock_credentials, db_session
            )
        
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_user_cookie_inactive_user(self, db_session):
        """Test that inactive user via cookie raises 403."""
        # Create inactive user
        auth_service = AuthService(db_session)
        password_hash = auth_service.get_password_hash("testpass")
        user = User(
            username="inactiveuser",
            email="inactive@example.com",
            password_hash=password_hash,
            is_active=0,  # Inactive!
            is_admin=1
        )
        db_session.add(user)
        await db_session.commit()
        
        # Create token
        token = auth_service.create_access_token(data={"sub": "inactiveuser"})
        
        # Mock request with cookie
        mock_request = Mock()
        mock_request.cookies = {"token": token}
        
        mock_credentials = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_with_cookie(
                mock_request, mock_credentials, db_session
            )
        
        assert exc_info.value.status_code == 403
        assert "Inactive user" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_user_cookie_nonexistent_user(self, db_session):
        """Test that cookie for non-existent user raises 401."""
        auth_service = AuthService(db_session)
        token = auth_service.create_access_token(data={"sub": "nonexistent"})
        
        mock_request = Mock()
        mock_request.cookies = {"token": token}
        
        mock_credentials = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_with_cookie(
                mock_request, mock_credentials, db_session
            )
        
        assert exc_info.value.status_code == 401
        assert "User not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_user_cookie_with_different_name(self, db_session):
        """Test that cookie with wrong name is ignored."""
        auth_service = AuthService(db_session)
        token = auth_service.create_access_token(data={"sub": "testuser"})
        
        mock_request = Mock()
        mock_request.cookies = {"wrong_cookie_name": token}  # Wrong name!
        
        mock_credentials = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_with_cookie(
                mock_request, mock_credentials, db_session
            )
        
        assert exc_info.value.status_code == 401


class TestSecurityEdgeCases:
    """Tests for edge cases and security vulnerabilities."""

    @pytest.mark.asyncio
    async def test_token_with_no_username(self, db_session):
        """Test that token without username is rejected."""
        # Create token with no 'sub' field
        from app.services.auth_service import AuthService
        import jwt
        from app.core.config import settings
        
        # Manually create token without 'sub'
        payload = {"data": "something", "exp": 9999999999}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        mock_credentials = Mock()
        mock_credentials.credentials = token
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, db_session)
        
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_malformed_jwt(self, db_session):
        """Test that malformed JWT is rejected."""
        mock_credentials = Mock()
        mock_credentials.credentials = "not.a.valid.jwt.structure.here"
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, db_session)
        
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_token(self, db_session):
        """Test that expired token is rejected."""
        from app.services.auth_service import AuthService
        from datetime import timedelta
        
        # Create user
        auth_service = AuthService(db_session)
        password_hash = auth_service.get_password_hash("testpass")
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=password_hash,
            is_active=1,
            is_admin=0
        )
        db_session.add(user)
        await db_session.commit()
        
        # Create token with negative expiration (expired)
        token = auth_service.create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(seconds=-100)  # Already expired
        )
        
        mock_credentials = Mock()
        mock_credentials.credentials = token
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, db_session)
        
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_token_with_wrong_secret(self, db_session):
        """Test that token signed with wrong secret is rejected."""
        import jwt
        from app.core.config import settings
        
        # Create token with wrong secret
        payload = {"sub": "testuser", "exp": 9999999999}
        token = jwt.encode(payload, "wrong-secret-key", algorithm=settings.ALGORITHM)
        
        mock_credentials = Mock()
        mock_credentials.credentials = token
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, db_session)
        
        assert exc_info.value.status_code == 401

