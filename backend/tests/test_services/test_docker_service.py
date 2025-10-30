"""Tests for Docker service."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import subprocess
from app.services.docker_service import DockerService


class TestDockerServiceInit:
    """Tests for DockerService initialization."""

    @patch('subprocess.run')
    def test_init_success(self, mock_run):
        """Test successful initialization when Docker is available."""
        mock_run.return_value = Mock(returncode=0)
        
        service = DockerService()
        
        assert service is not None
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["docker", "version"]

    @patch('subprocess.run')
    def test_init_docker_not_found(self, mock_run):
        """Test initialization fails when Docker command not found."""
        mock_run.side_effect = FileNotFoundError("docker: command not found")
        
        with pytest.raises(Exception, match="Docker is not available"):
            DockerService()

    @patch('subprocess.run')
    def test_init_docker_error(self, mock_run):
        """Test initialization fails when Docker returns error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker", stderr="error")
        
        with pytest.raises(Exception, match="Docker is not available"):
            DockerService()

    @patch('subprocess.run')
    def test_init_docker_timeout(self, mock_run):
        """Test initialization fails on timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("docker", 5)
        
        with pytest.raises(Exception, match="Docker is not available"):
            DockerService()


class TestListAllContainers:
    """Tests for list_all_containers method."""

    @patch('subprocess.run')
    def test_list_all_containers_success(self, mock_run):
        """Test listing all containers successfully."""
        # Mock docker version check
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        # Mock docker ps output
        container_json = json.dumps({
            "ID": "abc123def456",
            "Names": "docklite-backend",
            "Image": "backend:latest",
            "Status": "Up 2 hours",
            "Ports": "8000/tcp",
            "CreatedAt": "2024-01-01 10:00:00"
        })
        
        mock_run.return_value = Mock(
            stdout=container_json + "\n",
            returncode=0
        )
        
        containers = service.list_all_containers(all=True)
        
        assert len(containers) == 1
        assert containers[0]["name"] == "docklite-backend"
        assert containers[0]["image"] == "backend:latest"
        assert containers[0]["status"] == "running"
        assert containers[0]["is_system"] is True

    @patch('subprocess.run')
    def test_list_containers_running_only(self, mock_run):
        """Test listing only running containers."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.return_value = Mock(stdout="", returncode=0)
        
        containers = service.list_all_containers(all=False)
        
        # Check that --all flag was NOT added
        call_args = mock_run.call_args[0][0]
        assert "--all" not in call_args
        assert containers == []

    @patch('subprocess.run')
    def test_list_containers_with_project(self, mock_run):
        """Test container with project information."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        # Mock project container (docker-compose naming)
        container_json = json.dumps({
            "ID": "xyz789",
            "Names": "myproject_web_1",
            "Image": "nginx:alpine",
            "Status": "Up 1 hour",
            "Ports": "80/tcp",
            "CreatedAt": "2024-01-01 09:00:00"
        })
        
        mock_run.return_value = Mock(stdout=container_json + "\n", returncode=0)
        
        containers = service.list_all_containers()
        
        assert len(containers) == 1
        assert containers[0]["name"] == "myproject_web_1"
        assert containers[0]["project"] == "myproject"
        assert containers[0]["service"] == "web"
        assert containers[0]["is_system"] is False

    @patch('subprocess.run')
    def test_list_containers_empty(self, mock_run):
        """Test listing containers when none exist."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.return_value = Mock(stdout="", returncode=0)
        
        containers = service.list_all_containers()
        
        assert containers == []

    @patch('subprocess.run')
    def test_list_containers_command_error(self, mock_run):
        """Test error handling when docker ps fails."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "docker", stderr="permission denied"
        )
        
        with pytest.raises(Exception, match="Failed to list containers"):
            service.list_all_containers()

    @patch('subprocess.run')
    def test_list_containers_invalid_json(self, mock_run):
        """Test error handling with invalid JSON response."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.return_value = Mock(stdout="not valid json", returncode=0)
        
        with pytest.raises(Exception, match="Failed to list containers"):
            service.list_all_containers()


class TestGetContainer:
    """Tests for get_container method."""

    @patch('subprocess.run')
    def test_get_container_success(self, mock_run):
        """Test getting a specific container by ID."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        # Mock docker inspect output
        inspect_data = [{
            "Id": "abc123def456789",
            "Name": "/docklite-backend",
            "Config": {
                "Image": "backend:latest",
                "Labels": {
                    "com.docker.compose.project": "docklite",
                    "com.docker.compose.service": "backend"
                }
            },
            "State": {
                "Status": "running",
                "StartedAt": "2024-01-01T10:00:00Z"
            },
            "Created": "2024-01-01T09:00:00Z",
            "NetworkSettings": {
                "Ports": {
                    "8000/tcp": [{"HostIp": "0.0.0.0", "HostPort": "8000"}]
                }
            }
        }]
        
        mock_run.return_value = Mock(
            stdout=json.dumps(inspect_data),
            returncode=0
        )
        
        container = service.get_container("abc123")
        
        assert container is not None
        assert container["name"] == "docklite-backend"
        assert container["image"] == "backend:latest"
        assert container["status"] == "running"
        assert container["project"] == "docklite"
        assert container["service"] == "backend"
        assert container["is_system"] is True

    @patch('subprocess.run')
    def test_get_container_not_found(self, mock_run):
        """Test getting non-existent container."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker")
        
        container = service.get_container("nonexistent")
        
        assert container is None

    @patch('subprocess.run')
    def test_get_container_error(self, mock_run):
        """Test error handling in get_container."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.side_effect = Exception("Docker daemon not running")
        
        with pytest.raises(Exception, match="Failed to get container"):
            service.get_container("abc123")


class TestStartContainer:
    """Tests for start_container method."""

    @patch('subprocess.run')
    def test_start_container_success(self, mock_run):
        """Test successfully starting a container."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.return_value = Mock(returncode=0)
        
        success, error = service.start_container("mycontainer")
        
        assert success is True
        assert error is None
        # Verify correct command
        call_args = mock_run.call_args[0][0]
        assert call_args == ["docker", "start", "mycontainer"]

    @patch('subprocess.run')
    def test_start_container_error(self, mock_run):
        """Test error when starting container fails."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "docker", stderr="container not found"
        )
        
        success, error = service.start_container("nonexistent")
        
        assert success is False
        assert "container not found" in error

    @patch('subprocess.run')
    def test_start_container_timeout(self, mock_run):
        """Test timeout when starting container."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.side_effect = Exception("Timeout")
        
        success, error = service.start_container("mycontainer")
        
        assert success is False
        assert "Docker error" in error


class TestStopContainer:
    """Tests for stop_container method."""

    @patch('subprocess.run')
    def test_stop_container_success(self, mock_run):
        """Test successfully stopping a container."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.return_value = Mock(returncode=0)
        
        success, error = service.stop_container("mycontainer")
        
        assert success is True
        assert error is None
        # Verify timeout flag
        call_args = mock_run.call_args[0][0]
        assert "-t" in call_args
        assert "10" in call_args

    @patch('subprocess.run')
    def test_stop_container_custom_timeout(self, mock_run):
        """Test stopping container with custom timeout."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.return_value = Mock(returncode=0)
        
        success, error = service.stop_container("mycontainer", timeout=30)
        
        assert success is True
        call_args = mock_run.call_args[0][0]
        assert "30" in call_args

    @patch('subprocess.run')
    def test_stop_container_error(self, mock_run):
        """Test error when stopping container fails."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "docker", stderr="cannot stop"
        )
        
        success, error = service.stop_container("mycontainer")
        
        assert success is False
        assert "cannot stop" in error


class TestRestartContainer:
    """Tests for restart_container method."""

    @patch('subprocess.run')
    def test_restart_container_success(self, mock_run):
        """Test successfully restarting a container."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.return_value = Mock(returncode=0)
        
        success, error = service.restart_container("mycontainer")
        
        assert success is True
        assert error is None
        call_args = mock_run.call_args[0][0]
        assert call_args == ["docker", "restart", "-t", "10", "mycontainer"]

    @patch('subprocess.run')
    def test_restart_container_error(self, mock_run):
        """Test error when restarting container fails."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker")
        
        success, error = service.restart_container("mycontainer")
        
        assert success is False
        assert error is not None


class TestRemoveContainer:
    """Tests for remove_container method."""

    @patch('subprocess.run')
    def test_remove_container_success(self, mock_run):
        """Test successfully removing a container."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.return_value = Mock(returncode=0)
        
        success, error = service.remove_container("mycontainer")
        
        assert success is True
        assert error is None
        call_args = mock_run.call_args[0][0]
        assert call_args == ["docker", "rm", "mycontainer"]

    @patch('subprocess.run')
    def test_remove_container_force(self, mock_run):
        """Test force removing a container."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.return_value = Mock(returncode=0)
        
        success, error = service.remove_container("mycontainer", force=True)
        
        assert success is True
        call_args = mock_run.call_args[0][0]
        assert "-f" in call_args

    @patch('subprocess.run')
    def test_remove_container_error(self, mock_run):
        """Test error when removing container fails."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "docker", stderr="container is running"
        )
        
        success, error = service.remove_container("mycontainer")
        
        assert success is False
        assert "container is running" in error


class TestGetContainerLogs:
    """Tests for get_container_logs method."""

    @patch('subprocess.run')
    def test_get_logs_success(self, mock_run):
        """Test getting container logs successfully."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.return_value = Mock(
            stdout="log line 1\nlog line 2\n",
            stderr="",
            returncode=0
        )
        
        logs, error = service.get_container_logs("mycontainer")
        
        assert error is None
        assert "log line 1" in logs
        assert "log line 2" in logs

    @patch('subprocess.run')
    def test_get_logs_custom_tail(self, mock_run):
        """Test getting logs with custom tail count."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.return_value = Mock(stdout="logs", stderr="", returncode=0)
        
        logs, error = service.get_container_logs("mycontainer", tail=50)
        
        call_args = mock_run.call_args[0][0]
        assert "--tail" in call_args
        assert "50" in call_args

    @patch('subprocess.run')
    def test_get_logs_without_timestamps(self, mock_run):
        """Test getting logs without timestamps."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.return_value = Mock(stdout="logs", stderr="", returncode=0)
        
        logs, error = service.get_container_logs("mycontainer", timestamps=False)
        
        call_args = mock_run.call_args[0][0]
        assert "--timestamps" not in call_args

    @patch('subprocess.run')
    def test_get_logs_error(self, mock_run):
        """Test error when getting logs fails."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "docker", stderr="container not found"
        )
        
        logs, error = service.get_container_logs("nonexistent")
        
        assert logs is None
        assert "container not found" in error


class TestGetContainerStats:
    """Tests for get_container_stats method."""

    @patch('subprocess.run')
    def test_get_stats_success(self, mock_run):
        """Test getting container stats successfully."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        stats_json = json.dumps({
            "CPUPerc": "15.5%",
            "MemUsage": "100MiB / 2GiB",
            "MemPerc": "5.0%",
            "NetIO": "1.5kB / 2kB"
        })
        
        mock_run.return_value = Mock(stdout=stats_json, returncode=0)
        
        stats, error = service.get_container_stats("mycontainer")
        
        assert error is None
        assert stats["cpu_percent"] == 15.5
        assert stats["memory_usage"] == "100MiB"
        assert stats["memory_limit"] == "2GiB"
        assert stats["memory_percent"] == 5.0
        assert stats["network_io"] == "1.5kB / 2kB"

    @patch('subprocess.run')
    def test_get_stats_no_data(self, mock_run):
        """Test getting stats when no data available."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.return_value = Mock(stdout="", returncode=0)
        
        stats, error = service.get_container_stats("mycontainer")
        
        assert stats is None
        assert "No stats available" in error

    @patch('subprocess.run')
    def test_get_stats_error(self, mock_run):
        """Test error when getting stats fails."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker")
        
        stats, error = service.get_container_stats("mycontainer")
        
        assert stats is None
        assert error is not None


class TestSystemContainerProtection:
    """Tests for system container identification."""

    @patch('subprocess.run')
    def test_system_container_detection(self, mock_run):
        """Test that docklite- containers are marked as system."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        # Mock system container
        container_json = json.dumps({
            "ID": "sys123",
            "Names": "docklite-traefik",
            "Image": "traefik:v3.0",
            "Status": "Up 5 hours",
            "Ports": "80/tcp, 443/tcp",
            "CreatedAt": "2024-01-01 10:00:00"
        })
        
        mock_run.return_value = Mock(stdout=container_json + "\n", returncode=0)
        
        containers = service.list_all_containers()
        
        assert len(containers) == 1
        assert containers[0]["is_system"] is True
        assert containers[0]["name"] == "docklite-traefik"

    @patch('subprocess.run')
    def test_non_system_container_detection(self, mock_run):
        """Test that non-docklite containers are NOT marked as system."""
        mock_run.return_value = Mock(returncode=0)
        service = DockerService()
        
        # Mock user project container
        container_json = json.dumps({
            "ID": "usr123",
            "Names": "myapp-web-1",
            "Image": "nginx:alpine",
            "Status": "Up 1 hour",
            "Ports": "80/tcp",
            "CreatedAt": "2024-01-01 11:00:00"
        })
        
        mock_run.return_value = Mock(stdout=container_json + "\n", returncode=0)
        
        containers = service.list_all_containers()
        
        assert len(containers) == 1
        assert containers[0]["is_system"] is False

