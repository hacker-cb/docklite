"""
Hostname detection utility with priority logic
"""

import socket
from typing import Optional
from app.core.config import settings


def get_server_hostname(fallback: Optional[str] = None) -> str:
    """
    Get server hostname with priority logic:

    Priority 1: Config value (settings.HOSTNAME)
    Priority 2: System hostname (if valid)
    Priority 3: Fallback value or "localhost"

    Args:
        fallback: Optional fallback hostname (e.g., from HTTP Host header)

    Returns:
        Server hostname
    """
    # Priority 1: Config value
    if settings.HOSTNAME:
        return settings.HOSTNAME

    # Priority 2: System hostname
    try:
        system_hostname = socket.gethostname()
        if system_hostname and system_hostname != "localhost":
            # Validate that hostname is reasonable (not empty, not just IP)
            if system_hostname.strip() and not _is_ip_address(system_hostname):
                return system_hostname
    except Exception:
        pass

    # Priority 3: Fallback
    if fallback and fallback != "localhost":
        return fallback

    return "localhost"


def _is_ip_address(hostname: str) -> bool:
    """
    Check if hostname is an IP address

    Args:
        hostname: Hostname to check

    Returns:
        True if hostname is IP address
    """
    try:
        # Try to parse as IP
        parts = hostname.split(".")
        if len(parts) == 4:
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            return True
    except (ValueError, AttributeError):
        pass

    return False


def get_access_url(
    path: str = "", port: Optional[int] = None, protocol: str = "http"
) -> str:
    """
    Generate full access URL with hostname

    Args:
        path: URL path (e.g., "/api", "/docs")
        port: Optional port number
        protocol: Protocol (http or https)

    Returns:
        Full URL (e.g., "http://example.com/api" or "http://example.com:8888")
    """
    hostname = get_server_hostname()

    # Build URL
    url = f"{protocol}://{hostname}"

    # Add port if specified and not default
    if port and port not in (80, 443):
        url += f":{port}"

    # Add path
    if path:
        if not path.startswith("/"):
            path = "/" + path
        url += path

    return url
