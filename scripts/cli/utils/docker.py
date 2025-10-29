"""Docker and docker-compose utilities."""

import subprocess
import shutil
import grp
from pathlib import Path
from typing import List, Optional
from .console import log_error


def has_docker_group() -> bool:
    """Check if current user is in docker group."""
    try:
        docker_group = grp.getgrnam('docker')
        import os
        return docker_group.gr_gid in os.getgroups()
    except (KeyError, OSError):
        return False


def get_docker_compose_command() -> List[str]:
    """
    Get docker-compose command.
    
    Checks for:
    1. docker-compose (standalone)
    2. docker compose (plugin)
    
    Returns:
        List[str]: Command parts
    
    Raises:
        FileNotFoundError: If neither command is available
    """
    # Try docker-compose first
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    
    # Try docker compose
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return ["docker", "compose"]
    except FileNotFoundError:
        pass
    
    raise FileNotFoundError("docker-compose not found")


def docker_compose_cmd(
    *args: str,
    cwd: Optional[Path] = None,
    check: bool = True,
    capture_output: bool = False
) -> subprocess.CompletedProcess:
    """
    Execute docker-compose command.
    
    Args:
        *args: Arguments to pass to docker-compose
        cwd: Working directory
        check: Raise exception on error
        capture_output: Capture stdout/stderr
    
    Returns:
        CompletedProcess: Result of the command
    """
    cmd = get_docker_compose_command()
    cmd.extend(args)
    
    # Use sg docker if not in docker group
    if not has_docker_group():
        cmd = ["sg", "docker", "-c", " ".join(cmd)]
    
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        capture_output=capture_output,
        text=True
    )


def is_container_running(container_name: str) -> bool:
    """
    Check if a container is running.
    
    Args:
        container_name: Name of the container
    
    Returns:
        bool: True if running, False otherwise
    """
    try:
        if has_docker_group():
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                check=True
            )
        else:
            result = subprocess.run(
                ["sg", "docker", "-c", "docker ps --format '{{.Names}}'"],
                capture_output=True,
                text=True,
                check=True,
                shell=True
            )
        
        containers = result.stdout.strip().split('\n')
        return container_name in containers
    except subprocess.CalledProcessError:
        return False


def get_container_status() -> dict:
    """
    Get status of all DockLite containers.
    
    Returns:
        dict: Container name -> running status
    """
    from ..config import (
        CONTAINER_TRAEFIK,
        CONTAINER_BACKEND,
        CONTAINER_FRONTEND
    )
    
    return {
        "traefik": is_container_running(CONTAINER_TRAEFIK),
        "backend": is_container_running(CONTAINER_BACKEND),
        "frontend": is_container_running(CONTAINER_FRONTEND),
    }


def docker_exec(
    container: str,
    *command: str,
    capture_output: bool = True
) -> subprocess.CompletedProcess:
    """
    Execute command in Docker container.
    
    Args:
        container: Container name
        *command: Command to execute
        capture_output: Capture output
    
    Returns:
        CompletedProcess: Result
    """
    cmd = ["docker", "exec", "-T", container, *command]
    
    if not has_docker_group():
        cmd = ["sg", "docker", "-c", " ".join(cmd)]
    
    return subprocess.run(
        cmd,
        capture_output=capture_output,
        text=True
    )

