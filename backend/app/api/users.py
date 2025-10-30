from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.schemas import UserCreate
from app.services.auth_service import AuthService
from app.constants.messages import ErrorMessages, SuccessMessages
from app.utils.formatters import format_user_response

router = APIRouter(prefix="/users", tags=["users"])


def check_is_admin(current_user: User) -> None:
    """Check if current user is admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=ErrorMessages.ADMIN_REQUIRED
        )


@router.get("")
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[dict]:
    """Get all users (admin only)"""
    check_is_admin(current_user)

    result = await db.execute(select(User))
    users = result.scalars().all()

    return [format_user_response(u) for u in users]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Create a new user (admin only)"""
    check_is_admin(current_user)

    auth_service = AuthService(db)
    user, error = await auth_service.create_user(user_data)

    if error or not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error or "Failed to create user",
        )

    return format_user_response(user)


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Get user by ID (admin only)"""
    check_is_admin(current_user)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMessages.USER_NOT_FOUND
        )

    return format_user_response(user)


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    is_active: Optional[bool] = None,
    is_admin: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Update user (admin only)"""
    check_is_admin(current_user)

    # Cannot deactivate or remove admin from yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.CANNOT_MODIFY_SELF,
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMessages.USER_NOT_FOUND
        )

    if is_active is not None:
        setattr(user, "is_active", 1 if is_active else 0)

    if is_admin is not None:
        setattr(user, "is_admin", 1 if is_admin else 0)

    await db.commit()
    await db.refresh(user)

    return format_user_response(user)


@router.delete(
    "/{user_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Delete user (admin only)"""
    check_is_admin(current_user)

    # Cannot delete yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.CANNOT_DELETE_SELF,
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMessages.USER_NOT_FOUND
        )

    await db.delete(user)
    await db.commit()


@router.put("/{user_id}/password")
async def change_password(
    user_id: int,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Change user password (admin or self)"""
    # Admin can change any password, user can change only own
    if user_id != current_user.id:
        check_is_admin(current_user)

    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.PASSWORD_TOO_SHORT,
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMessages.USER_NOT_FOUND
        )

    # Hash new password
    auth_service = AuthService(db)
    setattr(user, "password_hash", auth_service.get_password_hash(new_password))

    await db.commit()

    return {"message": SuccessMessages.PASSWORD_CHANGED}
