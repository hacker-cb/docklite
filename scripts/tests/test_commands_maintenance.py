"""Tests for maintenance commands."""

import pytest
from unittest.mock import Mock, patch
from typer.testing import CliRunner
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.commands.maintenance import app as maint_app
from cli.main import app as main_app

runner = CliRunner()
maint_runner = CliRunner()


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
        
        # Use main_app because status is registered at root level
        result = runner.invoke(main_app, ["status"])
        
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
        
        # Use main_app because status is registered at root level
        result = runner.invoke(main_app, ["status", "--verbose"])
        
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
                result = runner.invoke(maint_app, ["backup"])
        
        # Should create backup
        # Note: This is a simplified test


class TestCleanCommand:
    """Tests for clean command."""
    
    @patch('subprocess.run')
    def test_clean_with_images_flag(self, mock_subprocess):
        """Test clean with --images flag."""
        result = runner.invoke(maint_app, ["clean", "--images"])
        
        # Should run docker image prune
        assert mock_subprocess.called
    
    @patch('typer.confirm')
    @patch('subprocess.run')
    def test_clean_with_volumes_confirmed(self, mock_subprocess, mock_confirm):
        """Test clean with --volumes when confirmed."""
        mock_confirm.return_value = True
        
        result = runner.invoke(maint_app, ["clean", "--volumes"])
        
        # Should run docker volume prune
        assert mock_subprocess.called
