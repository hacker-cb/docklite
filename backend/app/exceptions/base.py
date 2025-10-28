"""
Base exceptions
"""
from fastapi import status


class DockLiteException(Exception):
    """Base exception for DockLite application"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)


class NotFoundError(DockLiteException):
    """Resource not found exception"""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )


class AlreadyExistsError(DockLiteException):
    """Resource already exists exception"""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT
        )


class ValidationError(DockLiteException):
    """Validation error exception"""
    
    def __init__(self, message: str, field: str = None):
        detail = {"field": field} if field else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

