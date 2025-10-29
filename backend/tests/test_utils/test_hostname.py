"""
Tests for hostname utility
"""
import pytest
from unittest.mock import patch, MagicMock
from app.utils.hostname import get_server_hostname, _is_ip_address, get_access_url


class TestIsIpAddress:
    """Test IP address detection"""
    
    def test_valid_ipv4(self):
        """Test valid IPv4 addresses"""
        assert _is_ip_address("192.168.1.1") is True
        assert _is_ip_address("10.0.0.1") is True
        assert _is_ip_address("172.17.0.1") is True
        assert _is_ip_address("127.0.0.1") is True
    
    def test_invalid_ipv4(self):
        """Test invalid IPv4 addresses"""
        assert _is_ip_address("256.1.1.1") is False
        assert _is_ip_address("192.168.1") is False
        assert _is_ip_address("192.168.1.1.1") is False
    
    def test_domain_names(self):
        """Test domain names are not IPs"""
        assert _is_ip_address("example.com") is False
        assert _is_ip_address("localhost") is False
        assert _is_ip_address("server.example.com") is False
    
    def test_empty_string(self):
        """Test empty string"""
        assert _is_ip_address("") is False


class TestGetServerHostname:
    """Test hostname detection with priority logic"""
    
    def test_priority_1_config_value(self):
        """Test that config value has highest priority"""
        with patch('app.utils.hostname.settings') as mock_settings:
            mock_settings.HOSTNAME = "config.example.com"
            
            with patch('socket.gethostname', return_value="system.example.com"):
                hostname = get_server_hostname(fallback="fallback.example.com")
                assert hostname == "config.example.com"
    
    def test_priority_2_system_hostname(self):
        """Test that system hostname is used when config not set"""
        with patch('app.utils.hostname.settings') as mock_settings:
            mock_settings.HOSTNAME = None
            
            with patch('socket.gethostname', return_value="system.example.com"):
                hostname = get_server_hostname(fallback="fallback.example.com")
                assert hostname == "system.example.com"
    
    def test_priority_3_fallback(self):
        """Test that fallback is used when system hostname fails"""
        with patch('app.utils.hostname.settings') as mock_settings:
            mock_settings.HOSTNAME = None
            
            with patch('socket.gethostname', side_effect=Exception("Failed")):
                hostname = get_server_hostname(fallback="fallback.example.com")
                assert hostname == "fallback.example.com"
    
    def test_default_localhost(self):
        """Test that localhost is default when all else fails"""
        with patch('app.utils.hostname.settings') as mock_settings:
            mock_settings.HOSTNAME = None
            
            with patch('socket.gethostname', side_effect=Exception("Failed")):
                hostname = get_server_hostname(fallback=None)
                assert hostname == "localhost"
    
    def test_skips_localhost_hostname(self):
        """Test that system hostname 'localhost' is skipped"""
        with patch('app.utils.hostname.settings') as mock_settings:
            mock_settings.HOSTNAME = None
            
            with patch('socket.gethostname', return_value="localhost"):
                hostname = get_server_hostname(fallback="fallback.example.com")
                assert hostname == "fallback.example.com"
    
    def test_skips_ip_address_hostname(self):
        """Test that IP address hostnames are skipped"""
        with patch('app.utils.hostname.settings') as mock_settings:
            mock_settings.HOSTNAME = None
            
            with patch('socket.gethostname', return_value="192.168.1.1"):
                hostname = get_server_hostname(fallback="fallback.example.com")
                assert hostname == "fallback.example.com"
    
    def test_skips_empty_hostname(self):
        """Test that empty hostnames are skipped"""
        with patch('app.utils.hostname.settings') as mock_settings:
            mock_settings.HOSTNAME = None
            
            with patch('socket.gethostname', return_value="   "):
                hostname = get_server_hostname(fallback="fallback.example.com")
                assert hostname == "fallback.example.com"
    
    def test_fallback_localhost_ignored(self):
        """Test that fallback localhost is ignored in favor of default"""
        with patch('app.utils.hostname.settings') as mock_settings:
            mock_settings.HOSTNAME = None
            
            with patch('socket.gethostname', side_effect=Exception("Failed")):
                hostname = get_server_hostname(fallback="localhost")
                assert hostname == "localhost"


class TestGetAccessUrl:
    """Test URL generation"""
    
    def test_basic_url(self):
        """Test basic URL generation"""
        with patch('app.utils.hostname.get_server_hostname', return_value="example.com"):
            url = get_access_url()
            assert url == "http://example.com"
    
    def test_url_with_path(self):
        """Test URL with path"""
        with patch('app.utils.hostname.get_server_hostname', return_value="example.com"):
            url = get_access_url(path="/api")
            assert url == "http://example.com/api"
    
    def test_url_with_path_no_slash(self):
        """Test URL with path without leading slash"""
        with patch('app.utils.hostname.get_server_hostname', return_value="example.com"):
            url = get_access_url(path="api")
            assert url == "http://example.com/api"
    
    def test_url_with_custom_port(self):
        """Test URL with custom port"""
        with patch('app.utils.hostname.get_server_hostname', return_value="example.com"):
            url = get_access_url(port=8888)
            assert url == "http://example.com:8888"
    
    def test_url_with_port_and_path(self):
        """Test URL with port and path"""
        with patch('app.utils.hostname.get_server_hostname', return_value="example.com"):
            url = get_access_url(path="/dashboard", port=8888)
            assert url == "http://example.com:8888/dashboard"
    
    def test_url_https(self):
        """Test HTTPS URL"""
        with patch('app.utils.hostname.get_server_hostname', return_value="example.com"):
            url = get_access_url(protocol="https")
            assert url == "https://example.com"
    
    def test_url_port_80_not_shown(self):
        """Test that port 80 is not shown in URL"""
        with patch('app.utils.hostname.get_server_hostname', return_value="example.com"):
            url = get_access_url(port=80)
            assert url == "http://example.com"
    
    def test_url_port_443_not_shown(self):
        """Test that port 443 is not shown in HTTPS URL"""
        with patch('app.utils.hostname.get_server_hostname', return_value="example.com"):
            url = get_access_url(port=443, protocol="https")
            assert url == "https://example.com"

