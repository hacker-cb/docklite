"""Configuration and constants for DockLite CLI."""

import os
import socket
from pathlib import Path
from typing import Optional

# Version
VERSION = "1.0.0"

# Paths - Auto-detect based on script location
SCRIPTS_DIR = Path(__file__).parent.parent.absolute()  # scripts/cli -> scripts
PROJECT_ROOT = SCRIPTS_DIR.parent  # scripts -> project root
BACKEND_DATA_DIR = PROJECT_ROOT / "backend-data"
BACKUPS_DIR = PROJECT_ROOT / "backups"
ENV_FILE = PROJECT_ROOT / ".env"
DOCKER_COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"

# Default projects directory - use home directory for cross-platform compatibility
_home = Path.home()
DEFAULT_PROJECTS_DIR = _home / "docklite-projects"

# Container names
CONTAINER_TRAEFIK = "docklite-traefik"
CONTAINER_BACKEND = "docklite-backend"
CONTAINER_FRONTEND = "docklite-frontend"


def get_hostname() -> str:
    """
    Get server hostname with priority logic.
    
    Priority:
    1. HOSTNAME from .env file
    2. System hostname (if not localhost and not IP)
    3. Default to localhost
    
    Returns:
        str: Detected hostname
    """
    # Priority 1: HOSTNAME from .env file
    if ENV_FILE.exists():
        try:
            with open(ENV_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('HOSTNAME='):
                        hostname = line.split('=', 1)[1].strip().strip('"').strip("'")
                        if hostname:
                            return hostname
        except Exception:
            pass
    
    # Priority 2: System hostname (if valid)
    try:
        sys_hostname = socket.gethostname()
        if sys_hostname and sys_hostname != "localhost":
            # Check if it's not an IP address
            parts = sys_hostname.split('.')
            if not (len(parts) == 4 and all(part.isdigit() for part in parts)):
                return sys_hostname
    except Exception:
        pass
    
    # Priority 3: Default to localhost
    return "localhost"


def get_access_url(
    path: str = "",
    port: Optional[str] = None,
    protocol: str = "http"
) -> str:
    """
    Build access URL using detected hostname.
    
    Args:
        path: URL path (e.g., "/api")
        port: Port number (optional, omitted for 80/443)
        protocol: Protocol (default: "http")
    
    Returns:
        str: Complete URL
    """
    hostname = get_hostname()
    url = f"{protocol}://{hostname}"
    
    # Add port if specified and not default
    if port and port not in ("80", "443"):
        url = f"{url}:{port}"
    
    # Add path
    if path:
        if not path.startswith('/'):
            path = f"/{path}"
        url = f"{url}{path}"
    
    return url

