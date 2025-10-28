"""
Container management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.docker_service import DockerService
from app.models.project import Project

router = APIRouter()


class ContainerActionResponse(BaseModel):
    """Response for container actions"""
    success: bool
    message: str
    project_id: int


class ContainerStatusResponse(BaseModel):
    """Response for container status"""
    success: bool
    project_id: int
    running: bool
    containers: list
    raw_output: str = ""


@router.post("/{project_id}/start", response_model=ContainerActionResponse)
async def start_containers(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Start project containers (docker-compose up -d)
    """
    # Verify project exists
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    # Start containers
    docker_service = DockerService(project_id)
    success, message = await docker_service.start()
    
    if success:
        # Update project status
        await db.execute(
            update(Project).where(Project.id == project_id).values(status="running")
        )
        await db.commit()
    
    return ContainerActionResponse(
        success=success,
        message=message,
        project_id=project_id
    )


@router.post("/{project_id}/stop", response_model=ContainerActionResponse)
async def stop_containers(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Stop project containers (docker-compose down)
    """
    # Verify project exists
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    # Stop containers
    docker_service = DockerService(project_id)
    success, message = await docker_service.stop()
    
    if success:
        # Update project status
        await db.execute(
            update(Project).where(Project.id == project_id).values(status="stopped")
        )
        await db.commit()
    
    return ContainerActionResponse(
        success=success,
        message=message,
        project_id=project_id
    )


@router.post("/{project_id}/restart", response_model=ContainerActionResponse)
async def restart_containers(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Restart project containers (docker-compose restart)
    """
    # Verify project exists
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    # Restart containers
    docker_service = DockerService(project_id)
    success, message = await docker_service.restart()
    
    if success:
        # Update project status
        await db.execute(
            update(Project).where(Project.id == project_id).values(status="running")
        )
        await db.commit()
    
    return ContainerActionResponse(
        success=success,
        message=message,
        project_id=project_id
    )


@router.get("/{project_id}/status", response_model=ContainerStatusResponse)
async def get_container_status(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get container status (docker-compose ps)
    """
    # Verify project exists
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    # Get status
    docker_service = DockerService(project_id)
    success, status_data = await docker_service.get_status()
    
    if success:
        # Update project status in DB based on actual container status
        new_status = "running" if status_data.get("running") else "stopped"
        await db.execute(
            update(Project).where(Project.id == project_id).values(status=new_status)
        )
        await db.commit()
    
    return ContainerStatusResponse(
        success=success,
        project_id=project_id,
        running=status_data.get("running", False),
        containers=status_data.get("containers", []),
        raw_output=status_data.get("raw_output", "")
    )

