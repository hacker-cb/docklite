from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.schemas import UserCreate, UserResponse
from app.services.auth_service import AuthService
from typing import List

router = APIRouter(prefix="/users", tags=["users"])


def check_is_admin(current_user: User):
    """Check if current user is admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


@router.get("", response_model=List[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all users (admin only)"""
    check_is_admin(current_user)
    
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    return [
        UserResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            is_active=bool(u.is_active),
            is_admin=bool(u.is_admin),
            created_at=u.created_at
        )
        for u in users
    ]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new user (admin only)"""
    check_is_admin(current_user)
    
    auth_service = AuthService(db)
    user, error = await auth_service.create_user(user_data)
    
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=bool(user.is_active),
        is_admin=bool(user.is_admin),
        created_at=user.created_at
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user by ID (admin only)"""
    check_is_admin(current_user)
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=bool(user.is_active),
        is_admin=bool(user.is_admin),
        created_at=user.created_at
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    is_active: bool = None,
    is_admin: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user (admin only)"""
    check_is_admin(current_user)
    
    # Cannot deactivate or remove admin from yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own account"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if is_active is not None:
        user.is_active = 1 if is_active else 0
    
    if is_admin is not None:
        user.is_admin = 1 if is_admin else 0
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=bool(user.is_active),
        is_admin=bool(user.is_admin),
        created_at=user.created_at
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete user (admin only)"""
    check_is_admin(current_user)
    
    # Cannot delete yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    
    return None


@router.put("/{user_id}/password")
async def change_password(
    user_id: int,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Change user password (admin or self)"""
    # Admin can change any password, user can change only own
    if user_id != current_user.id:
        check_is_admin(current_user)
    
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Hash new password
    auth_service = AuthService(db)
    user.password_hash = auth_service.get_password_hash(new_password)
    
    await db.commit()
    
    return {"message": "Password changed successfully"}

