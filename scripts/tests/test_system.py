"""Tests for system utilities."""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path
import pwd

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.utils.system import (
    check_root,
    check_not_root,
    get_actual_user,
    get_actual_home,
    user_exists,
    backup_file
)


class TestCheckRoot:
    """Tests for check_root function."""
    
    def test_passes_when_root(self):
        """Test passes when running as root."""
        with patch('os.geteuid', return_value=0):
            check_root()  # Should not raise
    
    def test_raises_when_not_root(self):
        """Test raises PermissionError when not root."""
        with patch('os.geteuid', return_value=1000):
            with pytest.raises(PermissionError, match="must be run as root"):
                check_root()


class TestCheckNotRoot:
    """Tests for check_not_root function."""
    
    def test_passes_when_not_root(self):
        """Test passes when not running as root."""
        with patch('os.geteuid', return_value=1000):
            check_not_root()  # Should not raise
    
    def test_raises_when_root(self):
        """Test raises PermissionError when root."""
        with patch('os.geteuid', return_value=0):
            with pytest.raises(PermissionError, match="should NOT be run as root"):
                check_not_root()


class TestGetActualUser:
    """Tests for get_actual_user function."""
    
    def test_returns_sudo_user_when_set(self):
        """Test returns SUDO_USER when set."""
        with patch('os.environ.get') as mock_get:
            mock_get.side_effect = lambda k, d=None: "testuser" if k == "SUDO_USER" else d
            assert get_actual_user() == "testuser"
    
    def test_returns_user_when_sudo_user_not_set(self):
        """Test returns USER when SUDO_USER not set."""
        with patch('os.environ.get') as mock_get:
            mock_get.side_effect = lambda k, d=None: "currentuser" if k == "USER" else d
            assert get_actual_user() == "currentuser"


class TestGetActualHome:
    """Tests for get_actual_home function."""
    
    def test_returns_home_directory(self):
        """Test returns home directory."""
        with patch('cli.utils.system.get_actual_user', return_value="testuser"):
            mock_pwd = Mock()
            mock_pwd.pw_dir = "/home/testuser"
            with patch('pwd.getpwnam', return_value=mock_pwd):
                home = get_actual_home()
                assert home == Path("/home/testuser")
    
    def test_returns_current_home_on_error(self):
        """Test returns current home on error."""
        with patch('cli.utils.system.get_actual_user', return_value="testuser"):
            with patch('pwd.getpwnam', side_effect=KeyError("testuser")):
                home = get_actual_home()
                assert isinstance(home, Path)


class TestUserExists:
    """Tests for user_exists function."""
    
    def test_returns_true_for_existing_user(self):
        """Test returns True for existing user."""
        with patch('pwd.getpwnam', return_value=Mock()):
            assert user_exists("testuser") is True
    
    def test_returns_false_for_nonexistent_user(self):
        """Test returns False for nonexistent user."""
        with patch('pwd.getpwnam', side_effect=KeyError("testuser")):
            assert user_exists("testuser") is False


class TestBackupFile:
    """Tests for backup_file function."""
    
    def test_creates_backup_file(self, tmp_path):
        """Test creates backup file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        backup = backup_file(test_file, show_message=False)
        
        assert backup is not None
        assert backup.exists()
        assert backup.read_text() == "content"
    
    def test_returns_none_for_nonexistent_file(self, tmp_path):
        """Test returns None for nonexistent file."""
        test_file = tmp_path / "nonexistent.txt"
        
        backup = backup_file(test_file, show_message=False)
        
        assert backup is None

