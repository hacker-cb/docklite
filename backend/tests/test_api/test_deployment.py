"""Tests for deployment API endpoints"""
import pytest
from httpx import AsyncClient
from app.core.config import settings
from app.constants.messages import ErrorMessages


@pytest.mark.asyncio
async def test_get_deployment_info_success(client: AsyncClient, test_project, auth_headers, temp_projects_dir):
    """Test getting deployment info for existing project"""
    response = await client.get(
        f"/api/deployment/{test_project['id']}/info",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check basic fields
    assert data["project_id"] == test_project["id"]
    assert data["project_name"] == test_project["name"]
    assert data["domain"] == test_project["domain"]
    # deploy_user is now from owner.system_user
    assert "deploy_user" in data
    
    # Check project path contains slug
    assert "project_path" in data
    project_path = data["project_path"]
    # Path should contain slug, not just ID
    assert test_project["slug"] in project_path
    assert "/projects/" in project_path
    
    # Check instructions exist
    assert "instructions" in data
    instructions = data["instructions"]
    assert "upload_files" in instructions
    assert "start_containers" in instructions
    assert "check_status" in instructions
    assert "view_logs" in instructions
    assert "restart" in instructions
    assert "stop" in instructions
    
    # Verify instructions contain correct paths (with slug)
    assert test_project["slug"] in instructions["upload_files"]
    assert test_project["slug"] in instructions["start_containers"]
    
    # Check examples exist
    assert "examples" in data
    assert "deploy_script" in data["examples"]
    assert "ssh_config" in data["examples"]


@pytest.mark.asyncio
async def test_get_deployment_info_not_found(client: AsyncClient, auth_headers):
    """Test getting deployment info for non-existent project"""
    response = await client.get(
        "/api/deployment/99999/info",
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert ErrorMessages.PROJECT_NOT_FOUND in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_deployment_info_unauthorized(client: AsyncClient):
    """Test getting deployment info without authentication"""
    response = await client.get("/api/deployment/1/info")
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_ssh_setup_info(client: AsyncClient):
    """Test getting SSH setup instructions"""
    response = await client.get("/api/deployment/ssh-setup")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check basic fields
    assert "deploy_user" in data
    assert "projects_dir" in data
    assert data["deploy_user"] == getattr(settings, 'DEPLOY_USER', 'docklite')
    assert data["projects_dir"] == settings.PROJECTS_DIR
    
    # Check instructions exist
    assert "instructions" in data
    instructions = data["instructions"]
    assert "setup_server" in instructions
    assert "generate_key" in instructions
    assert "copy_key" in instructions
    assert "add_key" in instructions
    assert "test_connection" in instructions
    
    # Check documentation reference
    assert "documentation" in data


@pytest.mark.asyncio
async def test_deployment_info_contains_server_host(
    client: AsyncClient, 
    test_project, 
    auth_headers,
    temp_projects_dir
):
    """Test deployment info contains server hostname with priority logic"""
    # Make request with custom host header (now used as fallback only)
    headers = {**auth_headers, "host": "myserver.com:3000"}
    response = await client.get(
        f"/api/deployment/{test_project['id']}/info",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Server should be present and valid (could be system hostname or fallback)
    assert "server" in data
    assert data["server"]  # Not empty
    assert isinstance(data["server"], str)
    
    # Instructions should contain the server hostname
    server = data["server"]
    assert server in data["instructions"]["upload_files"]
    assert server in data["instructions"]["start_containers"]


@pytest.mark.asyncio
async def test_deployment_examples_format(client: AsyncClient, test_project, auth_headers, temp_projects_dir):
    """Test deployment examples are properly formatted"""
    response = await client.get(
        f"/api/deployment/{test_project['id']}/info",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check deploy script format
    deploy_script = data["examples"]["deploy_script"]
    assert "#!/bin/bash" in deploy_script
    assert "set -e" in deploy_script
    assert "rsync" in deploy_script
    assert "docker-compose up -d" in deploy_script
    
    # Check SSH config format
    ssh_config = data["examples"]["ssh_config"]
    assert "Host docklite-" in ssh_config
    assert "HostName" in ssh_config
    assert "User" in ssh_config
    assert "IdentityFile" in ssh_config

