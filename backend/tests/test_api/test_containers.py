"""Tests for containers API endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.asyncio
class TestContainersAPI:
    """Test containers management API."""
    
    @patch('app.api.containers.DockerService')
    async def test_list_containers_as_admin(self, mock_service_class, client: AsyncClient, admin_token):
        """Test listing containers as admin."""
        # Mock Docker service instance
        mock_instance = Mock()
        mock_instance.list_all_containers.return_value = [
            {
                'id': 'abc123',
                'name': 'test-container',
                'image': 'nginx:alpine',
                'status': 'running',
                'state': 'running',
                'created': '2025-10-29T10:00:00Z',
                'started': '2025-10-29T10:00:05Z',
                'ports': ['80/tcp'],
                'project': '',
                'service': '',
                'is_system': False,
                'labels': {}
            }
        ]
        mock_service_class.return_value = mock_instance
        
        response = await client.get(
            "/api/containers",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "containers" in data
        assert data["total"] == 1
        assert len(data["containers"]) == 1
        assert data["containers"][0]["name"] == "test-container"
        assert data["containers"][0]["status"] == "running"
    
    async def test_list_containers_without_auth(self, client: AsyncClient):
        """Test listing containers without authentication."""
        response = await client.get("/api/containers")
        # FastAPI HTTPBearer returns 403 when no credentials provided
        assert response.status_code == 403
    
    async def test_list_containers_as_non_admin(self, client: AsyncClient, user_token):
        """Test listing containers as non-admin user."""
        response = await client.get(
            "/api/containers",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()
    
    @patch('app.api.containers.DockerService')
    async def test_get_container_by_id(self, mock_service_class, client: AsyncClient, admin_token):
        """Test getting container by ID."""
        mock_instance = Mock()
        mock_instance.get_container.return_value = {
            'id': 'abc123',
            'name': 'test-container',
            'image': 'nginx:alpine',
            'status': 'running',
            'state': 'running',
            'created': '2025-10-29T10:00:00Z',
            'started': '2025-10-29T10:00:05Z',
            'ports': ['80/tcp'],
            'project': '',
            'service': '',
            'is_system': False,
            'labels': {}
        }
        mock_service_class.return_value = mock_instance
        
        response = await client.get(
            "/api/containers/abc123",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test-container"
        assert data["id"] == "abc123"
    
    @patch('app.api.containers.DockerService')
    async def test_get_container_not_found(self, mock_service_class, client: AsyncClient, admin_token):
        """Test getting non-existent container."""
        mock_instance = Mock()
        mock_instance.get_container.return_value = None
        mock_service_class.return_value = mock_instance
        
        response = await client.get(
            "/api/containers/nonexistent",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
    
    @patch('app.api.containers.DockerService')
    async def test_start_container(self, mock_service_class, client: AsyncClient, admin_token):
        """Test starting a container."""
        mock_instance = Mock()
        mock_instance.start_container.return_value = (True, None)
        mock_service_class.return_value = mock_instance
        
        response = await client.post(
            "/api/containers/abc123/start",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        assert "started successfully" in response.json()["detail"]
    
    @patch('app.api.containers.DockerService')
    async def test_start_container_failure(self, mock_service_class, client: AsyncClient, admin_token):
        """Test starting a container with error."""
        mock_instance = Mock()
        mock_instance.start_container.return_value = (False, "Container not found")
        mock_service_class.return_value = mock_instance
        
        response = await client.post(
            "/api/containers/abc123/start",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 400
        assert "Container not found" in response.json()["detail"]
    
    @patch('app.api.containers.DockerService')
    async def test_stop_container(self, mock_service_class, client: AsyncClient, admin_token):
        """Test stopping a container."""
        mock_instance = Mock()
        mock_instance.stop_container.return_value = (True, None)
        mock_service_class.return_value = mock_instance
        
        response = await client.post(
            "/api/containers/abc123/stop",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        assert "stopped successfully" in response.json()["detail"]
    
    @patch('app.api.containers.DockerService')
    async def test_restart_container(self, mock_service_class, client: AsyncClient, admin_token):
        """Test restarting a container."""
        mock_instance = Mock()
        mock_instance.restart_container.return_value = (True, None)
        mock_service_class.return_value = mock_instance
        
        response = await client.post(
            "/api/containers/abc123/restart",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        assert "restarted successfully" in response.json()["detail"]
    
    @patch('app.api.containers.DockerService')
    async def test_remove_container(self, mock_service_class, client: AsyncClient, admin_token):
        """Test removing a container."""
        mock_instance = Mock()
        mock_instance.remove_container.return_value = (True, None)
        mock_service_class.return_value = mock_instance
        
        response = await client.delete(
            "/api/containers/abc123",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        assert "removed successfully" in response.json()["detail"]
    
    @patch('app.api.containers.DockerService')
    async def test_remove_container_with_force(self, mock_service_class, client: AsyncClient, admin_token):
        """Test removing a running container with force."""
        mock_instance = Mock()
        mock_instance.remove_container.return_value = (True, None)
        mock_service_class.return_value = mock_instance
        
        response = await client.delete(
            "/api/containers/abc123?force=true",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        mock_instance.remove_container.assert_called_once_with('abc123', force=True)
    
    @patch('app.api.containers.DockerService')
    async def test_get_container_logs(self, mock_service_class, client: AsyncClient, admin_token):
        """Test getting container logs."""
        mock_instance = Mock()
        mock_instance.get_container_logs.return_value = (
            "2025-10-29 Log line 1\n2025-10-29 Log line 2\n",
            None
        )
        mock_service_class.return_value = mock_instance
        
        response = await client.get(
            "/api/containers/abc123/logs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "Log line 1" in data["logs"]
    
    @patch('app.api.containers.DockerService')
    async def test_get_container_logs_with_tail(self, mock_service_class, client: AsyncClient, admin_token):
        """Test getting container logs with custom tail."""
        mock_instance = Mock()
        mock_instance.get_container_logs.return_value = ("logs...", None)
        mock_service_class.return_value = mock_instance
        
        response = await client.get(
            "/api/containers/abc123/logs?tail=50",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        mock_instance.get_container_logs.assert_called_once_with('abc123', tail=50)
    
    @patch('app.api.containers.DockerService')
    async def test_get_container_stats(self, mock_service_class, client: AsyncClient, admin_token):
        """Test getting container stats."""
        mock_instance = Mock()
        mock_instance.get_container_stats.return_value = (
            {
                'cpu_percent': 25.5,
                'memory_usage': '100MiB',
                'memory_limit': '2GiB',
                'memory_percent': 5.0,
                'network_io': '1.5kB / 2kB'
            },
            None
        )
        mock_service_class.return_value = mock_instance
        
        response = await client.get(
            "/api/containers/abc123/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["stats"]["cpu_percent"] == 25.5
        assert data["stats"]["memory_percent"] == 5.0
    
    @patch('app.api.containers.DockerService')
    async def test_docker_service_error_handling(self, mock_service_class, client: AsyncClient, admin_token):
        """Test Docker service error handling."""
        mock_service_class.side_effect = Exception("Docker daemon not available")
        
        response = await client.get(
            "/api/containers",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 500
        assert "Docker daemon" in response.json()["detail"]
    
    @patch('app.api.containers.DockerService')
    async def test_logs_error_handling(self, mock_service_class, client: AsyncClient, admin_token):
        """Test logs error handling."""
        mock_instance = Mock()
        mock_instance.get_container_logs.return_value = (None, "Container not found")
        mock_service_class.return_value = mock_instance
        
        response = await client.get(
            "/api/containers/abc123/logs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 400
        assert "Container not found" in response.json()["detail"]
    
    @patch('app.api.containers.DockerService')
    async def test_stats_error_handling(self, mock_service_class, client: AsyncClient, admin_token):
        """Test stats error handling."""
        mock_instance = Mock()
        mock_instance.get_container_stats.return_value = (None, "Container not running")
        mock_service_class.return_value = mock_instance
        
        response = await client.get(
            "/api/containers/abc123/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 400
        assert "Container not running" in response.json()["detail"]
    
    # System Container Protection Tests
    
    async def test_cannot_stop_system_container_backend(self, client: AsyncClient, admin_token):
        """Test that backend system container cannot be stopped."""
        response = await client.post(
            "/api/containers/docklite-backend/stop",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 403
        assert 'Cannot stop system container' in response.json()['detail']
        assert 'docklite-backend' in response.json()['detail']
    
    async def test_cannot_stop_system_container_frontend(self, client: AsyncClient, admin_token):
        """Test that frontend system container cannot be stopped."""
        response = await client.post(
            "/api/containers/docklite-frontend/stop",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 403
        assert 'Cannot stop system container' in response.json()['detail']
    
    async def test_cannot_stop_system_container_traefik(self, client: AsyncClient, admin_token):
        """Test that traefik system container cannot be stopped."""
        response = await client.post(
            "/api/containers/docklite-traefik/stop",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 403
        assert 'Cannot stop system container' in response.json()['detail']
    
    async def test_cannot_restart_system_container(self, client: AsyncClient, admin_token):
        """Test that system containers cannot be restarted."""
        response = await client.post(
            "/api/containers/docklite-backend/restart",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 403
        assert 'Cannot restart system container' in response.json()['detail']
    
    async def test_cannot_remove_system_container(self, client: AsyncClient, admin_token):
        """Test that system containers cannot be removed."""
        response = await client.delete(
            "/api/containers/docklite-backend",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 403
        assert 'Cannot remove system container' in response.json()['detail']
    
    @patch('app.api.containers.DockerService')
    async def test_can_start_system_container(self, mock_service_class, client: AsyncClient, admin_token):
        """Test that system containers CAN be started (in case they're down)."""
        # Mock Docker service
        mock_instance = Mock()
        mock_instance.start_container.return_value = (True, None)
        mock_service_class.return_value = mock_instance
        
        response = await client.post(
            "/api/containers/docklite-backend/start",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Start should be allowed (for recovery)
        assert response.status_code == 200
        assert 'started successfully' in response.json()['detail']
    
    @patch('app.api.containers.DockerService')
    async def test_can_view_logs_system_container(self, mock_service_class, client: AsyncClient, admin_token):
        """Test that system container logs CAN be viewed (safe operation)."""
        # Mock Docker service
        mock_instance = Mock()
        mock_instance.get_container_logs.return_value = ("Log line 1\nLog line 2", None)
        mock_service_class.return_value = mock_instance
        
        response = await client.get(
            "/api/containers/docklite-backend/logs?tail=10",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Logs should be allowed
        assert response.status_code == 200
        assert 'logs' in response.json()
    
    @patch('app.api.containers.DockerService')
    async def test_can_stop_non_system_container(self, mock_service_class, client: AsyncClient, admin_token):
        """Test that non-system containers CAN be stopped."""
        # Mock Docker service
        mock_instance = Mock()
        mock_instance.stop_container.return_value = (True, None)
        mock_service_class.return_value = mock_instance
        
        response = await client.post(
            "/api/containers/my-project-web/stop",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Non-system containers should be stoppable
        assert response.status_code == 200
        assert 'stopped successfully' in response.json()['detail']
