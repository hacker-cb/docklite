from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_user_with_cookie
from app.models.schemas import UserLogin, Token, UserResponse, UserCreate
from app.services.auth_service import AuthService
from app.models.user import User
from app.constants.messages import ErrorMessages, SuccessMessages
from app.utils.formatters import format_user_response

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)) -> Token:
    """Login and get JWT token"""
    auth_service = AuthService(db)

    # Authenticate user
    user = await auth_service.authenticate_user(user_data.username, user_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessages.INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = auth_service.create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Get current user information"""
    return format_user_response(current_user)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)) -> dict:
    """Logout (client should remove token)"""
    return {"message": SuccessMessages.LOGOUT_SUCCESS}


@router.get("/setup/check")
async def check_setup_needed(db: AsyncSession = Depends(get_db)) -> dict:
    """Check if initial setup is needed (no users exist)"""
    auth_service = AuthService(db)
    has_users = await auth_service.has_users()

    return {"setup_needed": not has_users, "has_users": has_users}


@router.post("/setup")
async def initial_setup(
    user_data: UserCreate, db: AsyncSession = Depends(get_db)
) -> Token:
    """Create first admin user (only works if no users exist)"""
    auth_service = AuthService(db)

    # Create first admin
    user, error = await auth_service.create_first_admin(user_data)

    if error or not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error or "Failed to create admin",
        )

    # Auto-login: create access token
    access_token = auth_service.create_access_token(data={"sub": str(user.username)})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify-admin")
async def verify_admin(
    current_user: User = Depends(get_current_user_with_cookie),
) -> Response:
    """
    Verify that current user is an admin (for Traefik ForwardAuth)

    This endpoint is used by Traefik to protect admin-only resources like the dashboard.
    Supports JWT token from:
    1. Authorization header (Bearer token) - for API calls
    2. Cookie (token) - for browser dashboard access

    Returns 200 OK if user is admin, 403 Forbidden otherwise.

    Headers returned to Traefik:
    - X-User-Id: User ID
    - X-Username: Username
    - X-Is-Admin: true
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    # Return user info in headers for Traefik
    response = Response(status_code=200)
    response.headers["X-User-Id"] = str(current_user.id)
    response.headers["X-Username"] = str(current_user.username)
    response.headers["X-Is-Admin"] = "true"

    return response
