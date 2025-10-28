#!/usr/bin/env python3
"""CLI tool to create a new user for DockLite"""

import asyncio
import sys
from getpass import getpass
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.core.database import Base
from app.models.user import User
from app.models.schemas import UserCreate
from app.services.auth_service import AuthService


async def create_user_interactive():
    """Create user interactively"""
    print("=" * 50)
    print("DockLite - Create User")
    print("=" * 50)
    print()
    
    # Get user input
    username = input("Username (min 3 chars): ").strip()
    if len(username) < 3:
        print("❌ Username must be at least 3 characters")
        return False
    
    email = input("Email (optional, press Enter to skip): ").strip()
    if not email:
        email = None
    
    password = getpass("Password (min 6 chars): ")
    if len(password) < 6:
        print("❌ Password must be at least 6 characters")
        return False
    
    password_confirm = getpass("Confirm password: ")
    if password != password_confirm:
        print("❌ Passwords don't match")
        return False
    
    is_admin = input("Is admin? (y/N): ").strip().lower() == 'y'
    
    print()
    print(f"Creating user '{username}'...")
    
    # Create database connection
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthService(session)
        
        user_data = UserCreate(
            username=username,
            email=email,
            password=password
        )
        
        user, error = await auth_service.create_user(user_data)
        
        if error:
            print(f"❌ Error: {error}")
            return False
        
        # Update is_admin if needed
        if is_admin:
            user.is_admin = 1
            await session.commit()
        
        print(f"✅ User '{username}' created successfully!")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email or 'Not set'}")
        print(f"   Admin: {'Yes' if is_admin else 'No'}")
        print()
        
        return True
    
    await engine.dispose()


async def create_user_cli(username: str, password: str, email: str = None, is_admin: bool = False):
    """Create user from CLI arguments"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthService(session)
        
        user_data = UserCreate(
            username=username,
            email=email,
            password=password
        )
        
        user, error = await auth_service.create_user(user_data)
        
        if error:
            print(f"❌ Error: {error}")
            return False
        
        if is_admin:
            user.is_admin = 1
            await session.commit()
        
        print(f"✅ User '{username}' created successfully!")
        return True
    
    await engine.dispose()


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # CLI mode
        if len(sys.argv) < 3:
            print("Usage: python create_user.py <username> <password> [email] [--admin]")
            print("   Or: python create_user.py (interactive mode)")
            sys.exit(1)
        
        username = sys.argv[1]
        password = sys.argv[2]
        email = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else None
        is_admin = "--admin" in sys.argv
        
        success = asyncio.run(create_user_cli(username, password, email, is_admin))
    else:
        # Interactive mode
        success = asyncio.run(create_user_interactive())
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

