"""
Data formatting utilities
"""

import json
import re
from typing import Any
from app.models.project import Project
from app.models.user import User


def generate_slug_from_domain(domain: str, project_id: int) -> str:
    """
    Generate URL-safe slug from domain and project ID

    Args:
        domain: Domain name (e.g., "classly.ru", "my-site.com")
        project_id: Project ID

    Returns:
        str: Slug (e.g., "classly-ru-a3f9")
    """
    # Remove protocol if present
    domain = re.sub(r"^https?://", "", domain)

    # Remove port if present
    domain = re.sub(r":\d+$", "", domain)

    # Replace dots and non-alphanumeric chars with hyphens
    slug_base = re.sub(r"[^a-z0-9]+", "-", domain.lower())

    # Remove leading/trailing hyphens
    slug_base = slug_base.strip("-")

    # Generate short ID suffix (hex of project_id)
    short_id = format(project_id, "x")  # Convert to hex

    return f"{slug_base}-{short_id}"


def format_project_response(project: Project) -> dict:
    """
    Format project model to API response

    Args:
        project: Project model instance

    Returns:
        dict: Formatted project data
    """
    return {
        "id": project.id,
        "name": project.name,
        "domain": project.domain,
        "slug": project.slug,
        "owner_id": project.owner_id,
        "compose_content": project.compose_content,
        "env_vars": json.loads(project.env_vars or "{}"),
        "status": project.status,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }


def format_user_response(user: User) -> dict:
    """
    Format user model to API response

    Args:
        user: User model instance

    Returns:
        dict: Formatted user data
    """
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "system_user": user.system_user,
        "is_active": bool(user.is_active),
        "is_admin": bool(user.is_admin),
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string

    Args:
        json_str: JSON string
        default: Default value if parsing fails

    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default or {}


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    Safely serialize object to JSON

    Args:
        obj: Object to serialize
        default: Default value if serialization fails

    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(obj)
    except (TypeError, ValueError):
        return default
