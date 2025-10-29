"""
Authentication exceptions
"""

from fastapi import status
from .base import DockLiteException


class AuthenticationError(DockLiteException):
    """Authentication failed exception"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class PermissionDeniedError(DockLiteException):
    """Permission denied exception"""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


class InactiveUserError(DockLiteException):
    """User account is inactive exception"""

    def __init__(self, message: str = "User account is inactive"):
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)
