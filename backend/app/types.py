"""Type definitions for DockLite project."""

from __future__ import annotations

from typing import Literal

# Container operations
ContainerOperation = Literal["start", "stop", "restart", "remove"]

# Container states
ContainerState = Literal["running", "exited", "paused", "restarting", "dead"]

# Project statuses
ProjectStatus = Literal["created", "deployed", "error"]

# HTTP methods
HTTPMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]

# Log levels
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]