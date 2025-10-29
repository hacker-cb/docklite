"""
Tests for container management API endpoints
"""
import pytest
from unittest.mock import AsyncMock, patch


class TestContainers:
    """Test container management endpoints"""
    
    @pytest.mark.asyncio
    async def test_start_container_success(self, client, auth_headers, test_project):
        """Test starting container for a project"""
        # Use test_project fixture which creates project via API
        project_id = test_project["id"]
        
        # Mock DockerService
        with patch('app.api.containers.DockerService') as mock_docker:
            mock_instance = AsyncMock()
            mock_instance.start.return_value = (True, "Started successfully")
            mock_docker.return_value = mock_instance
            
            response = await client.post(
                f"/api/containers/{project_id}/start",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["project_id"] == project_id
    
    @pytest.mark.asyncio
    async def test_stop_container_success(self, client, auth_headers, test_project):
        """Test stopping container for a project"""
        # Use test_project fixture
        project_id = test_project["id"]
        
        
        # Mock DockerService
        with patch('app.api.containers.DockerService') as mock_docker:
            mock_instance = AsyncMock()
            mock_instance.stop.return_value = (True, "Stopped successfully")
            mock_docker.return_value = mock_instance
            
            response = await client.post(
                f"/api/containers/{project_id}/stop",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["project_id"] == project_id
    
    @pytest.mark.asyncio
    async def test_restart_container_success(self, client, auth_headers, test_project):
        """Test restarting container for a project"""
        # Use test_project fixture
        project_id = test_project["id"]
        
        # Mock DockerService
        with patch('app.api.containers.DockerService') as mock_docker:
            mock_instance = AsyncMock()
            mock_instance.restart.return_value = (True, "Restarted successfully")
            mock_docker.return_value = mock_instance
            
            response = await client.post(
                f"/api/containers/{project_id}/restart",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["project_id"] == project_id
    
    @pytest.mark.asyncio
    async def test_get_container_status(self, client, auth_headers, test_project):
        """Test getting container status"""
        # Use test_project fixture
        project_id = test_project["id"]
        
        # Mock DockerService
        with patch('app.api.containers.DockerService') as mock_docker:
            mock_instance = AsyncMock()
            mock_instance.get_status.return_value = (True, {
                "running": True,
                "containers": [
                    {"name": "test-project_web_1", "status": "running", "health": ""}
                ],
                "raw_output": "test-project_web_1   Up 5 minutes"
            })
            mock_docker.return_value = mock_instance
            
            response = await client.get(
                f"/api/containers/{project_id}/status",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["running"] is True
        assert len(data["containers"]) == 1
    
    @pytest.mark.asyncio
    async def test_container_action_project_not_found(self, client, auth_headers):
        """Test container action on non-existent project"""
        response = await client.post(
            "/api/containers/99999/start",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_container_action_unauthorized(self, client):
        """Test container action without authentication"""
        response = await client.post("/api/containers/1/start")
        
        # FastAPI returns 403 when auth dependency fails (no token provided)
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_container_start_failure(self, client, auth_headers, test_project):
        """Test handling of container start failure"""
        # Use test_project fixture
        project_id = test_project["id"]
        
        # Mock DockerService with failure
        with patch('app.api.containers.DockerService') as mock_docker:
            mock_instance = AsyncMock()
            mock_instance.start.return_value = (False, "Failed to start: connection refused")
            mock_docker.return_value = mock_instance
            
            response = await client.post(
                f"/api/containers/{project_id}/start",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Failed" in data["message"]

