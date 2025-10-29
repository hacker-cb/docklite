"""Tests for development commands."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.commands.development import app

runner = CliRunner()


class TestStartCommand:
    """Tests for start command."""
    
    @patch('cli.commands.development.check_docker')
    @patch('cli.commands.development.check_docker_compose')
    @patch('cli.commands.development.docker_compose_cmd')
    @patch('cli.commands.development.is_container_running')
    @patch('cli.commands.development.DEFAULT_PROJECTS_DIR')
    def test_start_basic(
        self,
        mock_projects_dir,
        mock_container,
        mock_docker_compose,
        mock_check_compose,
        mock_check_docker
    ):
        """Test basic start command."""
        mock_projects_dir.mkdir = Mock()
        mock_container.return_value = True
        
        result = runner.invoke(app, ["start"])
        
        # Should not fail
        mock_check_docker.assert_called_once()
        mock_check_compose.assert_called_once()
    
    @patch('cli.commands.development.check_docker')
    @patch('cli.commands.development.check_docker_compose')
    @patch('cli.commands.development.docker_compose_cmd')
    @patch('cli.commands.development.is_container_running')
    @patch('cli.commands.development.DEFAULT_PROJECTS_DIR')
    def test_start_with_build(
        self,
        mock_projects_dir,
        mock_container,
        mock_docker_compose,
        mock_check_compose,
        mock_check_docker
    ):
        """Test start with --build flag."""
        mock_projects_dir.mkdir = Mock()
        mock_container.return_value = True
        
        result = runner.invoke(app, ["start", "--build"])
        
        mock_check_docker.assert_called_once()


class TestStopCommand:
    """Tests for stop command."""
    
    @patch('cli.commands.development.docker_compose_cmd')
    def test_stop_basic(self, mock_docker_compose):
        """Test basic stop command."""
        result = runner.invoke(app, ["stop"])
        
        # Should call docker-compose down
        assert mock_docker_compose.called
    
    @patch('cli.commands.development.docker_compose_cmd')
    @patch('typer.confirm')
    def test_stop_with_volumes_confirmed(self, mock_confirm, mock_docker_compose):
        """Test stop with volumes when confirmed."""
        mock_confirm.return_value = True
        
        result = runner.invoke(app, ["stop", "--volumes"])
        
        assert mock_docker_compose.called


class TestLogsCommand:
    """Tests for logs command."""
    
    @patch('cli.commands.development.docker_compose_cmd')
    def test_logs_all_services(self, mock_docker_compose):
        """Test logs for all services."""
        result = runner.invoke(app, ["logs"])
        
        # Should call docker-compose logs
        assert mock_docker_compose.called
    
    @patch('cli.commands.development.docker_compose_cmd')
    def test_logs_specific_service(self, mock_docker_compose):
        """Test logs for specific service."""
        result = runner.invoke(app, ["logs", "backend"])
        
        # Should call docker-compose logs with service name
        assert mock_docker_compose.called


class TestVersionCommand:
    """Tests for version command."""
    
    def test_version_shows_correct_version(self):
        """Test version command shows correct version."""
        from cli.main import app as main_app
        
        result = runner.invoke(main_app, ["version"])
        
        assert "1.0.0" in result.stdout

