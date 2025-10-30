from __future__ import annotations

import json
from pathlib import Path
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.project import Project
from app.models.user import User
from app.models.schemas import ProjectCreate, ProjectUpdate
from app.validators import validate_docker_compose
from app.utils.formatters import generate_slug_from_domain
from app.constants.project_constants import ProjectStatus
from app.constants.messages import ErrorMessages
from app.services.traefik_service import TraefikService


class ProjectService:
    """Service for managing projects"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate_compose_content(
        self, compose_content: str
    ) -> tuple[bool, Optional[str]]:
        """Validate docker-compose.yml content"""
        return validate_docker_compose(compose_content)

    async def check_domain_unique(
        self, domain: str, exclude_id: Optional[int] = None
    ) -> bool:
        """Check if domain is unique"""
        query = select(Project).where(Project.domain == domain)
        if exclude_id:
            query = query.where(Project.id != exclude_id)

        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        return existing is None

    async def create_project(
        self, project_data: ProjectCreate, owner_id: int
    ) -> tuple[Optional[Project], Optional[str]]:
        """Create a new project"""
        # Validate compose content
        is_valid, error = await self.validate_compose_content(
            project_data.compose_content
        )
        if not is_valid:
            return None, f"{ErrorMessages.INVALID_COMPOSE}: {error}"

        # Check domain uniqueness
        if not await self.check_domain_unique(project_data.domain):
            return None, ErrorMessages.PROJECT_EXISTS

        # Get owner to determine system_user
        result = await self.db.execute(select(User).where(User.id == owner_id))
        owner = result.scalar_one_or_none()
        if not owner:
            return None, "Owner user not found"

        # Create project in database first to get ID
        env_vars_json = json.dumps(project_data.env_vars or {})

        new_project = Project(
            name=project_data.name,
            domain=project_data.domain,
            port=None,
            owner_id=owner_id,
            slug="",  # Will be set after flush
            compose_content=project_data.compose_content,
            env_vars=env_vars_json,
            status=ProjectStatus.CREATED,
        )

        self.db.add(new_project)
        await self.db.flush()  # Flush to get ID

        # Generate slug from domain and ID
        slug = generate_slug_from_domain(project_data.domain, int(new_project.id))
        setattr(new_project, "slug", slug)

        # Inject Traefik labels into compose content
        modified_compose, traefik_error = TraefikService.inject_labels_to_compose(
            project_data.compose_content, project_data.domain, slug
        )

        if traefik_error:
            await self.db.rollback()
            return None, f"Failed to inject Traefik labels: {traefik_error}"

        # Update compose_content with Traefik labels
        setattr(new_project, "compose_content", modified_compose)

        await self.db.commit()
        await self.db.refresh(new_project)

        # Create project directory in owner's home
        owner_home = f"/home/{owner.system_user}"
        project_dir = Path(owner_home) / "projects" / slug
        project_dir.mkdir(parents=True, exist_ok=True)

        # Write docker-compose.yml with Traefik labels
        compose_file = project_dir / "docker-compose.yml"
        compose_file.write_text(modified_compose)

        # Write .env file (always create, even if empty)
        env_file = project_dir / ".env"
        if project_data.env_vars:
            env_content = "\n".join(
                [f"{k}={v}" for k, v in project_data.env_vars.items()]
            )
            env_file.write_text(env_content)
        else:
            env_file.write_text("")  # Create empty .env file

        return new_project, None

    async def get_project_path(self, project: Project) -> Path:
        """Get project directory path"""
        result = await self.db.execute(select(User).where(User.id == project.owner_id))
        owner = result.scalar_one()
        owner_home = f"/home/{owner.system_user}"
        path: Path = Path(owner_home) / "projects" / project.slug
        return path

    async def get_project(
        self, project_id: int, user_id: Optional[int] = None, is_admin: bool = False
    ) -> Optional[Project]:
        """Get project by ID with ownership check"""
        query = select(Project).where(Project.id == project_id)

        # Non-admin users can only see their own projects
        if user_id and not is_admin:
            query = query.where(Project.owner_id == user_id)

        result = await self.db.execute(query)
        project: Optional[Project] = result.scalar_one_or_none()
        return project

    async def get_all_projects(
        self, user_id: Optional[int] = None, is_admin: bool = False
    ) -> list[Project]:
        """Get all projects (filtered by owner for non-admin)"""
        query = select(Project)

        # Non-admin users can only see their own projects
        if user_id and not is_admin:
            query = query.where(Project.owner_id == user_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_project(
        self,
        project_id: int,
        project_data: ProjectUpdate,
        user_id: Optional[int] = None,
        is_admin: bool = False,
    ) -> tuple[Optional[Project], Optional[str]]:
        """Update project"""
        project = await self.get_project(project_id, user_id, is_admin)
        if not project:
            return None, ErrorMessages.PROJECT_NOT_FOUND

        project_path = await self.get_project_path(project)

        compose_updated = False
        domain_updated = False

        # Validate compose content if provided
        if project_data.compose_content:
            is_valid, error = await self.validate_compose_content(
                project_data.compose_content
            )
            if not is_valid:
                return None, f"{ErrorMessages.INVALID_COMPOSE}: {error}"
            compose_updated = True

        # Update domain if provided
        if project_data.domain and project_data.domain != project.domain:
            if not await self.check_domain_unique(project_data.domain, project_id):
                return None, ErrorMessages.PROJECT_EXISTS
            domain_updated = True

        # If compose or domain changed, re-inject Traefik labels
        if compose_updated or domain_updated:
            new_compose = (
                project_data.compose_content
                if compose_updated
                else project.compose_content
            )
            new_domain = project_data.domain if domain_updated else project.domain

            modified_compose, traefik_error = TraefikService.inject_labels_to_compose(
                str(new_compose) if new_compose else "", 
                str(new_domain) if new_domain else "", 
                str(project.slug)
            )

            if traefik_error:
                return None, f"Failed to inject Traefik labels: {traefik_error}"

            setattr(project, "compose_content", modified_compose)

            # Update compose file
            compose_file = project_path / "docker-compose.yml"
            compose_file.write_text(modified_compose)

        # Update domain in DB
        if domain_updated:
            setattr(project, "domain", project_data.domain)

        # Update name if provided
        if project_data.name:
            setattr(project, "name", project_data.name)

        # Update env vars if provided
        if project_data.env_vars is not None:
            setattr(project, "env_vars", json.dumps(project_data.env_vars))

            # Update .env file
            env_file = project_path / ".env"
            if project_data.env_vars:
                env_content = "\n".join(
                    [f"{k}={v}" for k, v in project_data.env_vars.items()]
                )
                env_file.write_text(env_content)
            elif env_file.exists():
                env_file.unlink()

        await self.db.commit()
        await self.db.refresh(project)
        return project, None

    async def delete_project(
        self, project_id: int, user_id: Optional[int] = None, is_admin: bool = False
    ) -> tuple[bool, Optional[str]]:
        """Delete project"""
        project = await self.get_project(project_id, user_id, is_admin)
        if not project:
            return False, ErrorMessages.PROJECT_NOT_FOUND

        # Delete project files
        project_path = await self.get_project_path(project)
        if project_path.exists():
            import shutil

            shutil.rmtree(project_path)

        # Delete from database
        await self.db.delete(project)
        await self.db.commit()

        return True, None

    async def get_env_vars(
        self, project_id: int, user_id: Optional[int] = None, is_admin: bool = False
    ) -> Optional[dict[str, str]]:
        """Get project environment variables"""
        project = await self.get_project(project_id, user_id, is_admin)
        if not project:
            return None

        try:
            env_vars_str = str(project.env_vars) if project.env_vars else "{}"
            result: dict[str, str] = json.loads(env_vars_str)
            return result
        except BaseException:
            return {}

    async def update_env_vars(
        self,
        project_id: int,
        env_vars: dict[str, str],
        user_id: Optional[int] = None,
        is_admin: bool = False,
    ) -> tuple[bool, Optional[str]]:
        """Update project environment variables"""
        project = await self.get_project(project_id, user_id, is_admin)
        if not project:
            return False, ErrorMessages.PROJECT_NOT_FOUND

        setattr(project, "env_vars", json.dumps(env_vars))

        # Update .env file
        project_path = await self.get_project_path(project)
        project_path.mkdir(parents=True, exist_ok=True)
        env_file = project_path / ".env"

        if env_vars:
            env_content = "\n".join([f"{k}={v}" for k, v in env_vars.items()])
            env_file.write_text(env_content)
        elif env_file.exists():
            env_file.unlink()

        await self.db.commit()
        return True, None
