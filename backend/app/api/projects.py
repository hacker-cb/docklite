from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from app.core.database import get_db
from app.models.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.services.project_service import ProjectService
import json

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    service = ProjectService(db)
    new_project, error = await service.create_project(project)
    
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    # Parse env_vars back to dict
    new_project.env_vars = json.loads(new_project.env_vars or "{}")
    return new_project


@router.get("", response_model=ProjectListResponse)
async def get_projects(db: AsyncSession = Depends(get_db)):
    """Get all projects"""
    service = ProjectService(db)
    projects = await service.get_all_projects()
    
    # Parse env_vars for each project
    for project in projects:
        project.env_vars = json.loads(project.env_vars or "{}")
    
    return {
        "projects": projects,
        "total": len(projects)
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Get project by ID"""
    service = ProjectService(db)
    project = await service.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Parse env_vars
    project.env_vars = json.loads(project.env_vars or "{}")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update project"""
    service = ProjectService(db)
    updated_project, error = await service.update_project(project_id, project)
    
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    # Parse env_vars
    updated_project.env_vars = json.loads(updated_project.env_vars or "{}")
    return updated_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Delete project"""
    service = ProjectService(db)
    success, error = await service.delete_project(project_id)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    
    return None


@router.get("/{project_id}/env", response_model=Dict[str, str])
async def get_env_vars(project_id: int, db: AsyncSession = Depends(get_db)):
    """Get project environment variables"""
    service = ProjectService(db)
    env_vars = await service.get_env_vars(project_id)
    
    if env_vars is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    return env_vars


@router.put("/{project_id}/env")
async def update_env_vars(
    project_id: int,
    env_vars: Dict[str, str],
    db: AsyncSession = Depends(get_db)
):
    """Update project environment variables"""
    service = ProjectService(db)
    success, error = await service.update_env_vars(project_id, env_vars)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    
    return {"message": "Environment variables updated successfully"}

