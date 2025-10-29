"""
Project exceptions
"""

from .base import NotFoundError, AlreadyExistsError, ValidationError


class ProjectNotFoundError(NotFoundError):
    """Project not found exception"""

    def __init__(self, project_id: int = None):
        message = (
            f"Project {project_id} not found" if project_id else "Project not found"
        )
        super().__init__(message=message)


class ProjectExistsError(AlreadyExistsError):
    """Project already exists exception"""

    def __init__(self, domain: str = None):
        message = (
            f"Project with domain '{domain}' already exists"
            if domain
            else "Project already exists"
        )
        super().__init__(message=message)


class InvalidComposeError(ValidationError):
    """Invalid docker-compose content exception"""

    def __init__(self, details: str = None):
        message = (
            f"Invalid docker-compose.yml: {details}"
            if details
            else "Invalid docker-compose.yml content"
        )
        super().__init__(message=message, field="compose_content")
