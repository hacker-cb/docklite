"""Tests for Docker utilities."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.utils.docker import (
    has_docker_group,
    get_docker_compose_command,
    is_container_running,
    get_container_status
)


class TestHasDockerGroup:
    """Tests for has_docker_group function."""
    
    def test_returns_true_when_in_docker_group(self):
        """Test returns True when user is in docker group."""
        with patch('grp.getgrnam') as mock_grp:
            mock_grp.return_value = Mock(gr_gid=999)
            with patch('os.getgroups', return_value=[999, 1000]):
                assert has_docker_group() is True
    
    def test_returns_false_when_not_in_docker_group(self):
        """Test returns False when user is not in docker group."""
        with patch('shutil.which', return_value="/usr/bin/sg"):  # Mock sg command exists
            with patch('grp.getgrnam') as mock_grp:
                mock_grp.return_value = Mock(gr_gid=999)
                with patch('os.getgroups', return_value=[1000, 1001]):
                    assert has_docker_group() is False
    
    def test_returns_true_on_error(self):
        """Test returns True on error (skip group switching if docker group doesn't exist)."""
        with patch('shutil.which', return_value="/usr/bin/sg"):  # Mock sg command exists
            with patch('grp.getgrnam', side_effect=KeyError("docker")):
                # If docker group doesn't exist, return True to skip sg command
                assert has_docker_group() is True


class TestGetDockerComposeCommand:
    """Tests for get_docker_compose_command function."""
    
    def test_returns_docker_compose_when_available(self):
        """Test returns docker-compose when available."""
        with patch('shutil.which', return_value="/usr/bin/docker-compose"):
            assert get_docker_compose_command() == ["docker-compose"]
    
    def test_returns_docker_compose_plugin(self):
        """Test returns docker compose plugin."""
        with patch('shutil.which', return_value=None):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0)
                assert get_docker_compose_command() == ["docker", "compose"]
    
    def test_raises_error_when_not_available(self):
        """Test raises error when docker-compose not available."""
        with patch('shutil.which', return_value=None):
            with patch('subprocess.run', side_effect=FileNotFoundError()):
                with pytest.raises(FileNotFoundError):
                    get_docker_compose_command()


class TestIsContainerRunning:
    """Tests for is_container_running function."""
    
    def test_returns_true_for_running_container(self):
        """Test returns True for running container."""
        with patch('cli.utils.docker.has_docker_group', return_value=True):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    stdout="docklite-backend\ndocklite-frontend\n",
                    returncode=0
                )
                assert is_container_running("docklite-backend") is True
    
    def test_returns_false_for_stopped_container(self):
        """Test returns False for stopped container."""
        with patch('cli.utils.docker.has_docker_group', return_value=True):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    stdout="docklite-frontend\n",
                    returncode=0
                )
                assert is_container_running("docklite-backend") is False
    
    def test_returns_false_on_error(self):
        """Test returns False on error."""
        with patch('cli.utils.docker.has_docker_group', return_value=True):
            with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, [])):
                assert is_container_running("docklite-backend") is False


class TestGetContainerStatus:
    """Tests for get_container_status function."""
    
    def test_returns_status_dict(self):
        """Test returns dictionary with container statuses."""
        with patch('cli.utils.docker.is_container_running') as mock_running:
            mock_running.side_effect = [True, True, False]  # traefik, backend, frontend
            status = get_container_status()
            
            assert isinstance(status, dict)
            assert status["traefik"] is True
            assert status["backend"] is True
            assert status["frontend"] is False

