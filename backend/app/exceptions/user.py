"""
User exceptions
"""

from .base import NotFoundError, AlreadyExistsError


class UserNotFoundError(NotFoundError):
    """User not found exception"""

    def __init__(self, user_id: int = None, username: str = None):
        if user_id:
            message = f"User {user_id} not found"
        elif username:
            message = f"User '{username}' not found"
        else:
            message = "User not found"
        super().__init__(message=message)


class UsernameExistsError(AlreadyExistsError):
    """Username already exists exception"""

    def __init__(self, username: str):
        super().__init__(message=f"Username '{username}' already exists")
