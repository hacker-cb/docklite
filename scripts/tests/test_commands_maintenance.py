"""Tests for maintenance commands."""

import pytest
from unittest.mock import Mock, patch
from typer.testing import CliRunner
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.commands.maintenance import app

runner = CliRunner()


class TestStatusCommand:
    """Tests for status command."""
    
    @patch('cli.commands.maintenance.get_container_status')
    @patch('cli.commands.maintenance.docker_compose_cmd')
    def test_status_basic(self, mock_docker_compose, mock_status):
        """Test basic status command."""
        mock_status.return_value = {
            "traefik": True,
            "backend": True,
            "frontend": True
        }
        
        result = runner.invoke(app, ["status"])
        
        # Should show status
        assert mock_docker_compose.called
    
    @patch('cli.commands.maintenance.get_container_status')
    @patch('cli.commands.maintenance.docker_compose_cmd')
    @patch('subprocess.run')
    def test_status_verbose(self, mock_subprocess, mock_docker_compose, mock_status):
        """Test verbose status command."""
        mock_status.return_value = {
            "traefik": True,
            "backend": True,
            "frontend": True
        }
        
        result = runner.invoke(app, ["status", "--verbose"])
        
        # Verbose mode should show more info
        assert mock_docker_compose.called


class TestBackupCommand:
    """Tests for backup command."""
    
    @patch('cli.commands.maintenance.BACKUPS_DIR')
    @patch('tarfile.open')
    @patch('tempfile.TemporaryDirectory')
    def test_backup_creates_archive(self, mock_temp, mock_tarfile, mock_backups_dir):
        """Test backup creates archive."""
        mock_backups_dir.mkdir = Mock()
        mock_temp.return_value.__enter__.return_value = "/tmp/test"
        
        # Mock tarfile
        mock_tar = Mock()
        mock_tarfile.return_value.__enter__.return_value = mock_tar
        
        with patch('shutil.copy'):
            with patch('pathlib.Path.exists', return_value=True):
                result = runner.invoke(app, ["backup"])
        
        # Should create backup
        # Note: This is a simplified test


class TestCleanCommand:
    """Tests for clean command."""
    
    @patch('subprocess.run')
    def test_clean_with_images_flag(self, mock_subprocess):
        """Test clean with --images flag."""
        result = runner.invoke(app, ["clean", "--images"])
        
        # Should run docker image prune
        assert mock_subprocess.called
    
    @patch('typer.confirm')
    @patch('subprocess.run')
    def test_clean_with_volumes_confirmed(self, mock_subprocess, mock_confirm):
        """Test clean with --volumes when confirmed."""
        mock_confirm.return_value = True
        
        result = runner.invoke(app, ["clean", "--volumes"])
        
        # Should run docker volume prune
        assert mock_subprocess.called


class TestListUsersCommand:
    """Tests for list-users command."""
    
    @patch('cli.commands.maintenance.check_docker')
    @patch('cli.commands.maintenance.is_container_running')
    @patch('cli.commands.maintenance.docker_compose_cmd')
    def test_list_users_simple(self, mock_docker_compose, mock_container, mock_check):
        """Test list-users in simple mode."""
        mock_container.return_value = True
        mock_docker_compose.return_value = Mock(
            stdout="admin:admin:✓\n",
            returncode=0
        )
        
        result = runner.invoke(app, ["list-users"])
        
        # Should list users
        assert mock_docker_compose.called
    
    @patch('cli.commands.maintenance.check_docker')
    @patch('cli.commands.maintenance.is_container_running')
    @patch('cli.commands.maintenance.docker_compose_cmd')
    def test_list_users_verbose(self, mock_docker_compose, mock_container, mock_check):
        """Test list-users in verbose mode."""
        mock_container.return_value = True
        mock_docker_compose.return_value = Mock(
            stdout="1|admin|admin@example.com|admin|active|docklite\n",
            returncode=0
        )
        
        result = runner.invoke(app, ["list-users", "--verbose"])
        
        # Should show detailed table
        assert mock_docker_compose.called


class TestResetPasswordCommand:
    """Tests for reset-password command."""
    
    @patch('cli.commands.maintenance.check_docker')
    @patch('cli.commands.maintenance.is_container_running')
    @patch('cli.commands.maintenance.docker_compose_cmd')
    @patch('typer.prompt')
    def test_reset_password_interactive(
        self,
        mock_prompt,
        mock_docker_compose,
        mock_container,
        mock_check
    ):
        """Test reset-password in interactive mode."""
        mock_container.return_value = True
        
        # Mock user list
        mock_docker_compose.side_effect = [
            Mock(stdout="admin:admin\n", returncode=0),  # list users
            Mock(stdout="SUCCESS: Password reset for user 'admin'\nUser ID: 1\n", returncode=0)  # reset
        ]
        
        # Mock password prompts
        mock_prompt.side_effect = ["newpass123", "newpass123"]
        
        result = runner.invoke(app, ["reset-password", "admin"])
        
        # Should reset password
        assert mock_docker_compose.call_count >= 2

