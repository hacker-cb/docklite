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
from app.constants.messages import ErrorMessages, SuccessMessages
from app.constants.project_constants import ProjectStatus

router = APIRouter()


async def get_project_with_owner_check(
    project_id: int,
    current_user: User,
    db: AsyncSession
) -> tuple[Project, User]:
    """
    Get project and owner with ownership check
    
    Returns: (project, owner)
    Raises: HTTPException if project not found or access denied
    """
    # Get project
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.PROJECT_NOT_FOUND
        )
    
    # Check ownership (non-admin can only manage own projects)
    if not current_user.is_admin and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage your own projects"
        )
    
    # Get owner
    result = await db.execute(select(User).where(User.id == project.owner_id))
    owner = result.scalar_one()
    
    return project, owner


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
    project, owner = await get_project_with_owner_check(project_id, current_user, db)
    
    # Start containers
    docker_service = DockerService(project_id, project.slug, owner.system_user)
    success, message = await docker_service.start()
    
    if success:
        # Update project status
        await db.execute(
            update(Project).where(Project.id == project_id).values(status=ProjectStatus.RUNNING)
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
    project, owner = await get_project_with_owner_check(project_id, current_user, db)
    
    # Stop containers
    docker_service = DockerService(project_id, project.slug, owner.system_user)
    success, message = await docker_service.stop()
    
    if success:
        # Update project status
        await db.execute(
            update(Project).where(Project.id == project_id).values(status=ProjectStatus.STOPPED)
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
    project, owner = await get_project_with_owner_check(project_id, current_user, db)
    
    # Restart containers
    docker_service = DockerService(project_id, project.slug, owner.system_user)
    success, message = await docker_service.restart()
    
    if success:
        # Update project status
        await db.execute(
            update(Project).where(Project.id == project_id).values(status=ProjectStatus.RUNNING)
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
    project, owner = await get_project_with_owner_check(project_id, current_user, db)
    
    # Get status
    docker_service = DockerService(project_id, project.slug, owner.system_user)
    success, status_data = await docker_service.get_status()
    
    if success:
        # Update project status in DB based on actual container status
        new_status = ProjectStatus.RUNNING if status_data.get("running") else ProjectStatus.STOPPED
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

