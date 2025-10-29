"""List all users from database."""

import asyncio
import sys
import logging

# Disable SQLAlchemy logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

from app.core.database import AsyncSessionLocal
from app.models import user, project  # Import all models to avoid circular import issues
from app.models.user import User
from sqlalchemy import select, func


async def list_users_simple():
    """List users in simple format: username:role:status"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User.username, User.is_admin, User.is_active)
        )
        users = result.all()
        
        if not users:
            print('NO_USERS')
            return
        
        for username, is_admin, is_active in users:
            role = 'admin' if is_admin else 'user'
            status = '✓' if is_active else '✗'
            print(f'{username}:{role}:{status}')


async def list_users_detailed():
    """List users in detailed format: id|username|email|role|status|system_user"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(
                User.id,
                User.username,
                User.email,
                User.is_admin,
                User.is_active,
                User.system_user
            )
        )
        users = result.all()
        
        if not users:
            print('NO_USERS')
            return
        
        for user_id, username, email, is_admin, is_active, system_user in users:
            role = 'admin' if is_admin else 'user'
            status = 'active' if is_active else 'inactive'
            email_display = email or '-'
            sys_user = system_user or '-'
            print(f'{user_id}|{username}|{email_display}|{role}|{status}|{sys_user}')


async def count_users():
    """Count total users."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count(User.id)))
        count = result.scalar()
        print(count)


if __name__ == "__main__":
    # Parse command line arguments
    command = sys.argv[1] if len(sys.argv) > 1 else "simple"
    
    if command == "simple":
        asyncio.run(list_users_simple())
    elif command == "detailed":
        asyncio.run(list_users_detailed())
    elif command == "count":
        asyncio.run(count_users())
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)

