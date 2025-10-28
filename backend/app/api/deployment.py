from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.project_service import ProjectService
from app.core.config import settings
from app.constants.messages import ErrorMessages

router = APIRouter(prefix="/deployment", tags=["deployment"])


@router.get("/{project_id}/info")
async def get_deployment_info(
    project_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get deployment instructions for a project"""
    service = ProjectService(db)
    project = await service.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMessages.PROJECT_NOT_FOUND)
    
    # Get server hostname from request
    server_host = request.headers.get("host", "your-server").split(":")[0]
    
    deploy_user = getattr(settings, 'DEPLOY_USER', 'docklite')
    projects_dir = settings.PROJECTS_DIR
    project_path = f"{projects_dir}/{project_id}"
    
    return {
        "project_id": project_id,
        "project_name": project.name,
        "domain": project.domain,
        "project_path": project_path,
        "deploy_user": deploy_user,
        "server": server_host,
        "instructions": {
            "upload_files": f"rsync -avz ./your-app/ {deploy_user}@{server_host}:{project_path}/",
            "start_containers": f"ssh {deploy_user}@{server_host} \"cd {project_path} && docker-compose up -d\"",
            "check_status": f"ssh {deploy_user}@{server_host} \"cd {project_path} && docker-compose ps\"",
            "view_logs": f"ssh {deploy_user}@{server_host} \"cd {project_path} && docker-compose logs -f\"",
            "restart": f"ssh {deploy_user}@{server_host} \"cd {project_path} && docker-compose restart\"",
            "stop": f"ssh {deploy_user}@{server_host} \"cd {project_path} && docker-compose down\""
        },
        "examples": {
            "deploy_script": f"""#!/bin/bash
set -e

PROJECT_ID={project_id}
rsync -avz --exclude 'node_modules' --exclude '.git' \\
  ./ {deploy_user}@{server_host}:{project_path}/
ssh {deploy_user}@{server_host} \\
  "cd {project_path} && docker-compose up -d"
echo "✅ Deployed successfully!"
""",
            "ssh_config": f"""Host docklite-{project_id}
    HostName {server_host}
    User {deploy_user}
    IdentityFile ~/.ssh/id_ed25519
"""
        }
    }


@router.get("/ssh-setup")
async def get_ssh_setup_info():
    """Get SSH setup instructions"""
    deploy_user = getattr(settings, 'DEPLOY_USER', 'docklite')
    
    return {
        "deploy_user": deploy_user,
        "projects_dir": settings.PROJECTS_DIR,
        "instructions": {
            "setup_server": "cd /home/pavel/docklite && sudo ./setup-docklite-user.sh",
            "generate_key": "ssh-keygen -t ed25519 -C \"your_email@example.com\"",
            "copy_key": "cat ~/.ssh/id_ed25519.pub",
            "add_key": f"sudo -u {deploy_user} nano /home/{deploy_user}/.ssh/authorized_keys",
            "test_connection": f"ssh {deploy_user}@your-server"
        },
        "documentation": "/home/pavel/docklite/SSH_ACCESS.md"
    }

