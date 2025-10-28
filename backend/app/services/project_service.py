import json
import os
from pathlib import Path
from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.project import Project
from app.models.schemas import ProjectCreate, ProjectUpdate
from app.core.config import settings
from app.validators import validate_docker_compose
from app.constants.project_constants import ProjectStatus, DEFAULT_ENV_VARS
from app.constants.messages import ErrorMessages


class ProjectService:
    """Service for managing projects"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def validate_compose_content(self, compose_content: str) -> tuple[bool, Optional[str]]:
        """Validate docker-compose.yml content"""
        return validate_docker_compose(compose_content)
    
    async def check_domain_unique(self, domain: str, exclude_id: Optional[int] = None) -> bool:
        """Check if domain is unique"""
        query = select(Project).where(Project.domain == domain)
        if exclude_id:
            query = query.where(Project.id != exclude_id)
        
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        return existing is None
    
    
    async def create_project(self, project_data: ProjectCreate) -> tuple[Optional[Project], Optional[str]]:
        """Create a new project"""
        # Validate compose content
        is_valid, error = await self.validate_compose_content(project_data.compose_content)
        if not is_valid:
            return None, f"{ErrorMessages.INVALID_COMPOSE}: {error}"
        
        # Check domain uniqueness
        if not await self.check_domain_unique(project_data.domain):
            return None, ErrorMessages.PROJECT_EXISTS
        
        # Create project directory
        project_dir = Path(settings.PROJECTS_DIR)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create project in database
        env_vars_json = json.dumps(project_data.env_vars or {})
        
        new_project = Project(
            name=project_data.name,
            domain=project_data.domain,
            port=None,
            compose_content=project_data.compose_content,
            env_vars=env_vars_json,
            status=ProjectStatus.CREATED
        )
        
        self.db.add(new_project)
        await self.db.flush()  # Flush to get ID before file operations
        await self.db.commit()
        await self.db.refresh(new_project)
        
        # Create project directory and files
        project_path = project_dir / str(new_project.id)
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Write docker-compose.yml
        compose_file = project_path / "docker-compose.yml"
        compose_file.write_text(project_data.compose_content)
        
        # Write .env file
        if project_data.env_vars:
            env_file = project_path / ".env"
            env_content = "\n".join([f"{k}={v}" for k, v in project_data.env_vars.items()])
            env_file.write_text(env_content)
        
        return new_project, None
    
    async def get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()
    
    async def get_all_projects(self) -> List[Project]:
        """Get all projects"""
        result = await self.db.execute(select(Project))
        return list(result.scalars().all())
    
    async def update_project(self, project_id: int, project_data: ProjectUpdate) -> tuple[Optional[Project], Optional[str]]:
        """Update project"""
        project = await self.get_project(project_id)
        if not project:
            return None, ErrorMessages.PROJECT_NOT_FOUND
        
        # Validate compose content if provided
        if project_data.compose_content:
            is_valid, error = await self.validate_compose_content(project_data.compose_content)
            if not is_valid:
                return None, f"{ErrorMessages.INVALID_COMPOSE}: {error}"
            project.compose_content = project_data.compose_content
            
            # Update compose file
            project_path = Path(settings.PROJECTS_DIR) / str(project_id)
            compose_file = project_path / "docker-compose.yml"
            compose_file.write_text(project_data.compose_content)
        
        # Update domain if provided
        if project_data.domain and project_data.domain != project.domain:
            if not await self.check_domain_unique(project_data.domain, project_id):
                return None, ErrorMessages.PROJECT_EXISTS
            project.domain = project_data.domain
        
        # Update name if provided
        if project_data.name:
            project.name = project_data.name
        
        # Update env vars if provided
        if project_data.env_vars is not None:
            project.env_vars = json.dumps(project_data.env_vars)
            
            # Update .env file
            project_path = Path(settings.PROJECTS_DIR) / str(project_id)
            env_file = project_path / ".env"
            if project_data.env_vars:
                env_content = "\n".join([f"{k}={v}" for k, v in project_data.env_vars.items()])
                env_file.write_text(env_content)
            elif env_file.exists():
                env_file.unlink()
        
        await self.db.commit()
        await self.db.refresh(project)
        return project, None
    
    async def delete_project(self, project_id: int) -> tuple[bool, Optional[str]]:
        """Delete project"""
        project = await self.get_project(project_id)
        if not project:
            return False, ErrorMessages.PROJECT_NOT_FOUND
        
        # Delete project files
        project_path = Path(settings.PROJECTS_DIR) / str(project_id)
        if project_path.exists():
            import shutil
            shutil.rmtree(project_path)
        
        # Delete from database
        await self.db.delete(project)
        await self.db.commit()
        
        return True, None
    
    async def get_env_vars(self, project_id: int) -> Optional[Dict[str, str]]:
        """Get project environment variables"""
        project = await self.get_project(project_id)
        if not project:
            return None
        
        try:
            return json.loads(project.env_vars or "{}")
        except:
            return {}
    
    async def update_env_vars(self, project_id: int, env_vars: Dict[str, str]) -> tuple[bool, Optional[str]]:
        """Update project environment variables"""
        project = await self.get_project(project_id)
        if not project:
            return False, ErrorMessages.PROJECT_NOT_FOUND
        
        project.env_vars = json.dumps(env_vars)
        
        # Update .env file
        project_path = Path(settings.PROJECTS_DIR) / str(project_id)
        project_path.mkdir(parents=True, exist_ok=True)
        env_file = project_path / ".env"
        
        if env_vars:
            env_content = "\n".join([f"{k}={v}" for k, v in env_vars.items()])
            env_file.write_text(env_content)
        elif env_file.exists():
            env_file.unlink()
        
        await self.db.commit()
        return True, None

