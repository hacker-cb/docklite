"""
Project-related constants
"""
from enum import Enum


class ProjectStatus(str, Enum):
    """Project status enum"""
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


# Status descriptions
PROJECT_STATUS_MAP = {
    ProjectStatus.CREATED: "Project created, not deployed yet",
    ProjectStatus.RUNNING: "Project is running",
    ProjectStatus.STOPPED: "Project is stopped",
    ProjectStatus.ERROR: "Project encountered an error",
}


# Default values
DEFAULT_PROJECT_STATUS = ProjectStatus.CREATED
DEFAULT_ENV_VARS = "{}"

