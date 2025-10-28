"""
Data formatting utilities
"""
import json
from typing import Any
from app.models.project import Project
from app.models.user import User


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
        "compose_content": project.compose_content,
        "env_vars": json.loads(project.env_vars or "{}"),
        "status": project.status,
        "created_at": project.created_at,
        "updated_at": project.updated_at
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
        "is_active": bool(user.is_active),
        "is_admin": bool(user.is_admin),
        "created_at": user.created_at
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

