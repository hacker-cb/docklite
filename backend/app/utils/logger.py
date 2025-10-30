"""
Logging utilities
"""

import logging
from typing import Optional
from fastapi import Request


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        logging.Logger: Logger instance
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


def log_request(request: Request, logger: Optional[logging.Logger] = None) -> None:
    """
    Log incoming request

    Args:
        request: FastAPI request object
        logger: Logger instance (optional)
    """
    if logger is None:
        logger = get_logger(__name__)

    logger.info(
        f"{request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'Unknown'}"
    )


def log_error(
    error: Exception,
    context: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
) -> None:
    """
    Log error with context

    Args:
        error: Exception object
        context: Additional context
        logger: Logger instance (optional)
    """
    if logger is None:
        logger = get_logger(__name__)

    message = f"Error: {str(error)}"
    if context:
        message = f"{context} - {message}"

    logger.error(message, exc_info=True)
