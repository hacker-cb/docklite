from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.services.project_service import ProjectService
from app.utils.formatters import format_project_response
from app.constants.messages import ErrorMessages, SuccessMessages

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Create a new project (owned by current user)"""
    service = ProjectService(db)
    new_project, error = await service.create_project(
        project, owner_id=int(current_user.id)
    )

    if error or not new_project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return format_project_response(new_project)


@router.get("", response_model=ProjectListResponse)
async def get_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Get all projects (filtered by ownership for non-admin)"""
    service = ProjectService(db)
    projects = await service.get_all_projects(
        user_id=int(current_user.id), is_admin=bool(current_user.is_admin)
    )

    return {
        "projects": [format_project_response(p) for p in projects],
        "total": len(projects),
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Get project by ID (with ownership check)"""
    service = ProjectService(db)
    project = await service.get_project(
        project_id, user_id=int(current_user.id), is_admin=bool(current_user.is_admin)
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.PROJECT_NOT_FOUND,
        )

    return format_project_response(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Update project (with ownership check)"""
    service = ProjectService(db)
    updated_project, error = await service.update_project(
        project_id,
        project,
        user_id=int(current_user.id),
        is_admin=bool(current_user.is_admin),
    )

    if error or not updated_project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return format_project_response(updated_project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Delete project (with ownership check)"""
    service = ProjectService(db)
    success, error = await service.delete_project(
        project_id, user_id=int(current_user.id), is_admin=bool(current_user.is_admin)
    )

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)

    return None


@router.get("/{project_id}/env", response_model=Dict[str, str])
async def get_env_vars(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get project environment variables (with ownership check)"""
    service = ProjectService(db)
    env_vars = await service.get_env_vars(
        project_id, user_id=current_user.id, is_admin=bool(current_user.is_admin)
    )

    if env_vars is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.PROJECT_NOT_FOUND,
        )

    return env_vars


@router.put("/{project_id}/env")
async def update_env_vars(
    project_id: int,
    env_vars: Dict[str, str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update project environment variables (with ownership check)"""
    service = ProjectService(db)
    success, error = await service.update_env_vars(
        project_id,
        env_vars,
        user_id=current_user.id,
        is_admin=bool(current_user.is_admin),
    )

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)

    return {"message": SuccessMessages.ENV_VARS_UPDATED}
