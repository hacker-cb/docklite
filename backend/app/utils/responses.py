"""
API response utilities
"""

from typing import Any, Optional
from fastapi.responses import JSONResponse


def success_response(
    data: Any = None, message: str = None, status_code: int = 200
) -> dict:
    """
    Create a standardized success response

    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code

    Returns:
        dict: Formatted response
    """
    response = {"success": True, "data": data}

    if message:
        response["message"] = message

    return response


def error_response(
    message: str, status_code: int = 400, details: Optional[dict] = None
) -> JSONResponse:
    """
    Create a standardized error response

    Args:
        message: Error message
        status_code: HTTP status code
        details: Additional error details

    Returns:
        JSONResponse: Formatted error response
    """
    content = {"success": False, "detail": message}

    if details:
        content["details"] = details

    return JSONResponse(status_code=status_code, content=content)


def paginated_response(
    items: list, total: int, page: int = 1, page_size: int = 10
) -> dict:
    """
    Create a paginated response

    Args:
        items: List of items
        total: Total number of items
        page: Current page number
        page_size: Items per page

    Returns:
        dict: Paginated response
    """
    total_pages = (total + page_size - 1) // page_size

    return {
        "success": True,
        "data": {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        },
    }
