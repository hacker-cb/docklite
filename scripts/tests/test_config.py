"""Tests for config module."""

import pytest
from pathlib import Path
from unittest.mock import mock_open, patch
import sys

# Add cli to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.config import get_hostname, get_access_url, PROJECT_ROOT


class TestGetHostname:
    """Tests for get_hostname function."""
    
    def test_returns_hostname_from_env_file(self, tmp_path):
        """Test hostname from .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("HOSTNAME=example.com\n")
        
        with patch('cli.config.ENV_FILE', env_file):
            assert get_hostname() == "example.com"
    
    def test_returns_system_hostname_when_no_env(self):
        """Test system hostname when .env doesn't exist."""
        with patch('cli.config.ENV_FILE', Path("/nonexistent/.env")):
            with patch('socket.gethostname', return_value="myserver"):
                hostname = get_hostname()
                # Should return system hostname or localhost
                assert hostname in ["myserver", "localhost"]
    
    def test_returns_localhost_for_ip_hostname(self):
        """Test returns localhost for IP hostname."""
        with patch('cli.config.ENV_FILE', Path("/nonexistent/.env")):
            with patch('socket.gethostname', return_value="192.168.1.1"):
                assert get_hostname() == "localhost"
    
    def test_returns_localhost_as_fallback(self):
        """Test localhost as fallback."""
        with patch('cli.config.ENV_FILE', Path("/nonexistent/.env")):
            with patch('socket.gethostname', side_effect=Exception("No hostname")):
                assert get_hostname() == "localhost"


class TestGetAccessUrl:
    """Tests for get_access_url function."""
    
    def test_basic_url(self):
        """Test basic URL without path."""
        with patch('cli.config.get_hostname', return_value="example.com"):
            assert get_access_url() == "http://example.com"
    
    def test_url_with_path(self):
        """Test URL with path."""
        with patch('cli.config.get_hostname', return_value="example.com"):
            assert get_access_url("/api") == "http://example.com/api"
    
    def test_url_with_path_no_slash(self):
        """Test URL adds slash to path."""
        with patch('cli.config.get_hostname', return_value="example.com"):
            assert get_access_url("api") == "http://example.com/api"
    
    def test_url_with_non_standard_port(self):
        """Test URL with non-standard port."""
        with patch('cli.config.get_hostname', return_value="example.com"):
            assert get_access_url("", "8080") == "http://example.com:8080"
    
    def test_url_hides_port_80(self):
        """Test URL hides port 80."""
        with patch('cli.config.get_hostname', return_value="example.com"):
            assert get_access_url("", "80") == "http://example.com"
    
    def test_url_hides_port_443(self):
        """Test URL hides port 443."""
        with patch('cli.config.get_hostname', return_value="example.com"):
            assert get_access_url("", "443") == "http://example.com"
    
    def test_url_with_https(self):
        """Test URL with HTTPS protocol."""
        with patch('cli.config.get_hostname', return_value="example.com"):
            assert get_access_url("/secure", protocol="https") == "https://example.com/secure"


class TestConstants:
    """Tests for module constants."""
    
    def test_project_root_is_path(self):
        """Test PROJECT_ROOT is a Path object."""
        assert isinstance(PROJECT_ROOT, Path)
    
    def test_project_root_exists(self):
        """Test PROJECT_ROOT directory exists."""
        assert PROJECT_ROOT.exists()

