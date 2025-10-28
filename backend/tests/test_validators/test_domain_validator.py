"""Tests for domain validator"""
import pytest
from app.validators.domain_validator import validate_domain, is_valid_domain


class TestValidateDomain:
    """Test validate_domain function"""
    
    def test_valid_domain(self):
        """Test validation of valid domain names"""
        valid_domains = [
            "example.com",
            "subdomain.example.com",
            "my-site.example.org",
            "api.v2.example.io",
            "test123.example.co.uk"
        ]
        
        for domain in valid_domains:
            is_valid, error = validate_domain(domain)
            assert is_valid is True, f"Domain {domain} should be valid"
            assert error == ""
    
    def test_localhost(self):
        """Test validation allows localhost"""
        valid_locals = ["localhost", "127.0.0.1", "0.0.0.0"]
        
        for local in valid_locals:
            is_valid, error = validate_domain(local)
            assert is_valid is True, f"{local} should be valid"
            assert error == ""
    
    def test_ip_addresses(self):
        """Test validation allows valid IP addresses"""
        valid_ips = [
            "192.168.1.1",
            "10.0.0.1",
            "172.16.0.1",
            "8.8.8.8",
            "255.255.255.255"
        ]
        
        for ip in valid_ips:
            is_valid, error = validate_domain(ip)
            assert is_valid is True, f"IP {ip} should be valid"
            assert error == ""
    
    def test_domain_with_port(self):
        """Test validation strips port numbers"""
        is_valid, error = validate_domain("example.com:8080")
        assert is_valid is True
        assert error == ""
        
        is_valid, error = validate_domain("192.168.1.1:3000")
        assert is_valid is True
        assert error == ""
    
    def test_empty_domain(self):
        """Test validation fails for empty domain"""
        is_valid, error = validate_domain("")
        assert is_valid is False
        assert "cannot be empty" in error
    
    def test_whitespace_domain(self):
        """Test validation fails for whitespace-only domain"""
        is_valid, error = validate_domain("   ")
        assert is_valid is False
        assert "cannot be empty" in error
    
    def test_too_long_domain(self):
        """Test validation fails for domains exceeding 255 characters"""
        long_domain = "a" * 256 + ".com"
        is_valid, error = validate_domain(long_domain)
        assert is_valid is False
        assert "too long" in error
    
    def test_invalid_domain_format(self):
        """Test validation fails for invalid domain formats"""
        invalid_domains = [
            "invalid_domain",  # underscore not allowed
            "-example.com",    # starts with dash
            "example-.com",    # ends with dash
            "example..com",    # double dot
            ".example.com",    # starts with dot
            "example.com.",    # ends with dot (after strip)
            "example",         # no TLD
            "exam ple.com"     # space
        ]
        
        for domain in invalid_domains:
            is_valid, error = validate_domain(domain)
            assert is_valid is False, f"Domain {domain} should be invalid"
            assert "Invalid domain format" in error
    
    def test_case_insensitive(self):
        """Test validation is case-insensitive"""
        is_valid, error = validate_domain("EXAMPLE.COM")
        assert is_valid is True
        assert error == ""


class TestIsValidDomain:
    """Test is_valid_domain function"""
    
    def test_valid_domain_returns_true(self):
        """Test is_valid_domain returns True for valid domains"""
        assert is_valid_domain("example.com") is True
        assert is_valid_domain("sub.example.org") is True
        assert is_valid_domain("localhost") is True
        assert is_valid_domain("192.168.1.1") is True
    
    def test_invalid_domain_returns_false(self):
        """Test is_valid_domain returns False for invalid domains"""
        assert is_valid_domain("") is False
        assert is_valid_domain("invalid_domain") is False
        assert is_valid_domain("example") is False

