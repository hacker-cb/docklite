"""
Docker Compose validation
"""

import yaml
from typing import Optional, Tuple
from app.exceptions import InvalidComposeError


def validate_docker_compose(compose_content: str) -> Tuple[bool, Optional[str]]:
    """
    Validate docker-compose.yml content

    Args:
        compose_content: Docker compose YAML content

    Returns:
        Tuple of (is_valid, error_message or None)
    """
    if not compose_content or not compose_content.strip():
        return False, "Docker Compose content cannot be empty"

    try:
        compose_data = yaml.safe_load(compose_content)
    except yaml.YAMLError as e:
        return False, f"Invalid YAML syntax: {str(e)}"

    if not isinstance(compose_data, dict):
        return False, "Docker Compose must be a YAML object"

    if "services" not in compose_data:
        return False, "Docker Compose must contain 'services' section"

    if not isinstance(compose_data["services"], dict):
        return False, "'services' must be a dictionary"

    if not compose_data["services"]:
        return False, "'services' section cannot be empty"

    return True, None


def is_valid_compose(compose_content: str, raise_exception: bool = False) -> bool:
    """
    Check if docker-compose content is valid

    Args:
        compose_content: Docker compose YAML content
        raise_exception: If True, raises InvalidComposeError on validation failure

    Returns:
        bool: True if valid

    Raises:
        InvalidComposeError: If raise_exception=True and validation fails
    """
    is_valid, error_msg = validate_docker_compose(compose_content)

    if not is_valid and raise_exception:
        raise InvalidComposeError(error_msg)

    return is_valid
