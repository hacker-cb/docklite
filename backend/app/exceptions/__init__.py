"""
Custom exceptions for DockLite API
"""

from .base import DockLiteException, NotFoundError, AlreadyExistsError, ValidationError
from .auth import AuthenticationError, PermissionDeniedError, InactiveUserError
from .project import ProjectNotFoundError, ProjectExistsError, InvalidComposeError
from .user import UserNotFoundError, UsernameExistsError

__all__ = [
    # Base
    "DockLiteException",
    "NotFoundError",
    "AlreadyExistsError",
    "ValidationError",
    # Auth
    "AuthenticationError",
    "PermissionDeniedError",
    "InactiveUserError",
    # Project
    "ProjectNotFoundError",
    "ProjectExistsError",
    "InvalidComposeError",
    # User
    "UserNotFoundError",
    "UsernameExistsError",
]
