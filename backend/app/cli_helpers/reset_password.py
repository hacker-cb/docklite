"""Reset user password."""

from sqlalchemy import text
from passlib.context import CryptContext

# Import all models to avoid circular import issues
from app.core.database import AsyncSessionLocal
import asyncio
import sys
import logging

# Disable SQLAlchemy logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def check_user_exists(username: str) -> bool:
    """Check if user exists."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT id FROM users WHERE username = :username"),
            {"username": username},
        )
        return result.fetchone() is not None


async def list_all_users():
    """List all users (for error messages)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT username, is_admin FROM users"))
        users = result.all()

        if not users:
            print("NO_USERS")
            return

        for username, is_admin in users:
            role = "admin" if is_admin else "user"
            print(f"{username}:{role}")


async def reset_password(username: str, new_password: str) -> bool:
    """Reset user password. Returns True if successful, False otherwise."""
    async with AsyncSessionLocal() as session:
        # Find user
        result = await session.execute(
            text(
                "SELECT id, username, email, is_admin, is_active FROM users WHERE username = :username"
            ),
            {"username": username},
        )
        user_row = result.fetchone()

        if not user_row:
            print(f"ERROR: User '{username}' not found")
            return False

        # Hash new password
        password_hash = pwd_context.hash(new_password)

        # Update password
        await session.execute(
            text("UPDATE users SET password_hash = :hash WHERE username = :username"),
            {"hash": password_hash, "username": username},
        )
        await session.commit()

        # Print success info
        print(f"SUCCESS: Password reset for user '{username}'")
        print(f"User ID: {user_row[0]}")
        print(f"Email: {user_row[2] or 'N/A'}")
        print(f"Admin: {'Yes' if user_row[3] else 'No'}")
        print(f"Active: {'Yes' if user_row[4] else 'No'}")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: reset_password.py <command> [args]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == "check":
        # Check if user exists
        if len(sys.argv) < 3:
            print("Usage: reset_password.py check <username>", file=sys.stderr)
            sys.exit(1)
        username = sys.argv[2]
        exists = asyncio.run(check_user_exists(username))
        sys.exit(0 if exists else 1)

    elif command == "list":
        # List all users
        asyncio.run(list_all_users())

    elif command == "reset":
        # Reset password
        if len(sys.argv) < 4:
            print(
                "Usage: reset_password.py reset <username> <password>", file=sys.stderr
            )
            sys.exit(1)
        username = sys.argv[2]
        password = sys.argv[3]
        success = asyncio.run(reset_password(username, password))
        sys.exit(0 if success else 1)

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)
