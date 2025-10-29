"""Validation utilities for Docker and system checks."""

import shutil
import subprocess
from .console import log_error


def check_docker():
    """
    Check if Docker is installed and running.
    
    Raises:
        SystemExit: If Docker is not available or not running
    """
    # Check if docker command exists
    if not shutil.which("docker"):
        log_error("Docker is not installed")
        raise SystemExit(1)
    
    # Check if Docker daemon is running
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            check=False
        )
        if result.returncode != 0:
            log_error("Docker is not running")
            raise SystemExit(1)
    except Exception as e:
        log_error(f"Failed to check Docker: {e}")
        raise SystemExit(1)


def check_docker_compose():
    """
    Check if docker-compose is available.
    
    Raises:
        SystemExit: If docker-compose is not available
    """
    # Check for docker-compose command
    if shutil.which("docker-compose"):
        return
    
    # Check for docker compose plugin
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            check=False
        )
        if result.returncode == 0:
            return
    except Exception:
        pass
    
    log_error("docker-compose is not installed")
    raise SystemExit(1)

