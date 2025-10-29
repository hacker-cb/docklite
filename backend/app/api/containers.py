"""API endpoints for Docker containers management."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.core.security import get_current_active_user
from app.models.user import User
from app.services.docker_service import DockerService
from app.constants.messages import ErrorMessages, SuccessMessages


router = APIRouter(prefix="/containers", tags=["containers"])


def check_is_admin(current_user: User):
    """Check if current user is admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorMessages.ADMIN_REQUIRED
        )


@router.get("")
async def list_containers(
    all: bool = True,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of all Docker containers (admin only).
    
    Args:
        all: If True, show all containers. If False, show only running.
        current_user: Current authenticated user
        
    Returns:
        List of containers with their details
    """
    check_is_admin(current_user)
    
    try:
        docker_service = DockerService()
        containers = docker_service.list_all_containers(all=all)
        return {"containers": containers, "total": len(containers)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list containers: {str(e)}"
        )


@router.get("/{container_id}")
async def get_container(
    container_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get details of a specific container (admin only).
    
    Args:
        container_id: Container ID or name
        current_user: Current authenticated user
        
    Returns:
        Container details
    """
    check_is_admin(current_user)
    
    try:
        docker_service = DockerService()
        container = docker_service.get_container(container_id)
        
        if not container:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Container '{container_id}' not found"
            )
        
        return container
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get container: {str(e)}"
        )


@router.post("/{container_id}/start")
async def start_container(
    container_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Start a container (admin only).
    
    Args:
        container_id: Container ID or name
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    check_is_admin(current_user)
    
    try:
        docker_service = DockerService()
        success, error = docker_service.start_container(container_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        return {"detail": f"Container '{container_id}' started successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start container: {str(e)}"
        )


@router.post("/{container_id}/stop")
async def stop_container(
    container_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Stop a container (admin only).
    
    Args:
        container_id: Container ID or name
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    check_is_admin(current_user)
    
    try:
        docker_service = DockerService()
        success, error = docker_service.stop_container(container_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        return {"detail": f"Container '{container_id}' stopped successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop container: {str(e)}"
        )


@router.post("/{container_id}/restart")
async def restart_container(
    container_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Restart a container (admin only).
    
    Args:
        container_id: Container ID or name
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    check_is_admin(current_user)
    
    try:
        docker_service = DockerService()
        success, error = docker_service.restart_container(container_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        return {"detail": f"Container '{container_id}' restarted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restart container: {str(e)}"
        )


@router.delete("/{container_id}")
async def remove_container(
    container_id: str,
    force: bool = False,
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove a container (admin only).
    
    Args:
        container_id: Container ID or name
        force: Force remove even if running
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    check_is_admin(current_user)
    
    try:
        docker_service = DockerService()
        success, error = docker_service.remove_container(container_id, force=force)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        return {"detail": f"Container '{container_id}' removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove container: {str(e)}"
        )


@router.get("/{container_id}/logs")
async def get_container_logs(
    container_id: str,
    tail: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get container logs (admin only).
    
    Args:
        container_id: Container ID or name
        tail: Number of lines from the end (default 100)
        current_user: Current authenticated user
        
    Returns:
        Container logs
    """
    check_is_admin(current_user)
    
    try:
        docker_service = DockerService()
        logs, error = docker_service.get_container_logs(container_id, tail=tail)
        
        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        return {"logs": logs}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get logs: {str(e)}"
        )


@router.get("/{container_id}/stats")
async def get_container_stats(
    container_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get container resource usage statistics (admin only).
    
    Args:
        container_id: Container ID or name
        current_user: Current authenticated user
        
    Returns:
        Container stats (CPU, memory, network)
    """
    check_is_admin(current_user)
    
    try:
        docker_service = DockerService()
        stats, error = docker_service.get_container_stats(container_id)
        
        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )
