"""
Docker/Docker Compose management service
Executes docker-compose commands via SSH on the deployment server
"""
import asyncio
import logging
from typing import Dict, List, Optional
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class DockerService:
    """Service for managing Docker containers via docker-compose"""
    
    def __init__(self, project_id: int, project_dir: Optional[Path] = None):
        """
        Initialize DockerService for a specific project
        
        Args:
            project_id: ID of the project
            project_dir: Path to project directory (defaults to /home/{DEPLOY_USER}/projects/{project_id})
        """
        self.project_id = project_id
        if project_dir:
            self.project_dir = project_dir
        else:
            self.project_dir = Path(settings.PROJECTS_BASE_DIR) / str(project_id)
    
    async def _run_ssh_command(self, command: str) -> tuple[int, str, str]:
        """
        Execute command via SSH on deployment server
        
        Args:
            command: Command to execute
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        ssh_cmd = [
            "ssh",
            f"{settings.DEPLOY_USER}@{settings.DEPLOY_HOST}",
            "-p", str(settings.DEPLOY_PORT),
            command
        ]
        
        logger.info(f"Executing SSH command: {' '.join(ssh_cmd)}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *ssh_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            return_code = process.returncode or 0
            
            stdout_str = stdout.decode('utf-8').strip()
            stderr_str = stderr.decode('utf-8').strip()
            
            if return_code != 0:
                logger.error(f"SSH command failed: {stderr_str}")
            else:
                logger.info(f"SSH command succeeded: {stdout_str}")
            
            return return_code, stdout_str, stderr_str
            
        except Exception as e:
            logger.error(f"SSH command exception: {e}")
            return 1, "", str(e)
    
    async def _run_docker_compose(self, action: str) -> tuple[bool, str]:
        """
        Run docker-compose command
        
        Args:
            action: Docker Compose action (up -d, down, restart, ps, etc.)
            
        Returns:
            Tuple of (success, message)
        """
        command = f"cd {self.project_dir} && docker-compose {action}"
        return_code, stdout, stderr = await self._run_ssh_command(command)
        
        if return_code == 0:
            return True, stdout
        else:
            return False, stderr or "Command failed"
    
    async def start(self) -> tuple[bool, str]:
        """
        Start project containers (docker-compose up -d)
        
        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Starting containers for project {self.project_id}")
        return await self._run_docker_compose("up -d")
    
    async def stop(self) -> tuple[bool, str]:
        """
        Stop project containers (docker-compose down)
        
        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Stopping containers for project {self.project_id}")
        return await self._run_docker_compose("down")
    
    async def restart(self) -> tuple[bool, str]:
        """
        Restart project containers (docker-compose restart)
        
        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Restarting containers for project {self.project_id}")
        return await self._run_docker_compose("restart")
    
    async def get_status(self) -> tuple[bool, Dict]:
        """
        Get container status (docker-compose ps)
        
        Returns:
            Tuple of (success, status_dict)
            status_dict: {
                "running": bool,
                "containers": [{"name": "...", "status": "..."}],
                "raw_output": "..."
            }
        """
        logger.info(f"Getting status for project {self.project_id}")
        
        # Use docker-compose ps --format json for structured output
        success, output = await self._run_docker_compose("ps --format json")
        
        if not success:
            return False, {"running": False, "containers": [], "raw_output": output}
        
        # Parse JSON output
        import json
        containers = []
        running = False
        
        try:
            # docker-compose ps --format json outputs one JSON object per line
            for line in output.split('\n'):
                if line.strip():
                    container = json.loads(line)
                    containers.append({
                        "name": container.get("Name", ""),
                        "status": container.get("State", ""),
                        "health": container.get("Health", "")
                    })
                    if container.get("State") == "running":
                        running = True
        except json.JSONDecodeError:
            # Fallback: parse text output
            lines = output.split('\n')
            for line in lines:
                if 'Up' in line:
                    running = True
                    parts = line.split()
                    if parts:
                        containers.append({
                            "name": parts[0],
                            "status": "running",
                            "health": ""
                        })
        
        return True, {
            "running": running,
            "containers": containers,
            "raw_output": output
        }
    
    async def get_logs(self, tail: int = 100, follow: bool = False) -> tuple[bool, str]:
        """
        Get container logs (docker-compose logs)
        
        Args:
            tail: Number of lines to show
            follow: Whether to follow logs (stream)
            
        Returns:
            Tuple of (success, logs)
        """
        logger.info(f"Getting logs for project {self.project_id}")
        
        action = f"logs --tail={tail}"
        if follow:
            action += " -f"
        
        return await self._run_docker_compose(action)

