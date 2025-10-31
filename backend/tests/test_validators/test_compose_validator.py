"""Tests for Docker Compose validator"""
import pytest
from app.validators.compose_validator import validate_docker_compose, is_valid_compose
from app.exceptions import InvalidComposeError


class TestValidateDockerCompose:
    """Test validate_docker_compose function"""
    
    def test_valid_compose(self):
        """Test validation of valid docker-compose content"""
        compose_content = """
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
"""
        is_valid, error = validate_docker_compose(compose_content)
        assert is_valid is True
        assert error is None
    
    def test_empty_content(self):
        """Test validation fails for empty content"""
        is_valid, error = validate_docker_compose("")
        assert is_valid is False
        assert error is not None
        assert "cannot be empty" in error
    
    def test_whitespace_only(self):
        """Test validation fails for whitespace-only content"""
        is_valid, error = validate_docker_compose("   \n  \t  ")
        assert is_valid is False
        assert error is not None
        assert "cannot be empty" in error
    
    def test_invalid_yaml(self):
        """Test validation fails for invalid YAML syntax"""
        compose_content = """
services:
  web:
    image: nginx
    ports: [[[[[  # Invalid YAML syntax
"""
        is_valid, error = validate_docker_compose(compose_content)
        assert is_valid is False
        assert error is not None
        assert "Invalid YAML syntax" in error
    
    def test_non_dict_yaml(self):
        """Test validation fails for non-dictionary YAML"""
        compose_content = "- item1\n- item2"
        is_valid, error = validate_docker_compose(compose_content)
        assert is_valid is False
        assert error is not None
        assert "must be a YAML object" in error
    
    def test_missing_services(self):
        """Test validation fails when services section is missing"""
        compose_content = """
version: '3.8'
networks:
  mynet:
"""
        is_valid, error = validate_docker_compose(compose_content)
        assert is_valid is False
        assert error is not None
        assert "must contain 'services' section" in error
    
    def test_services_not_dict(self):
        """Test validation fails when services is not a dictionary"""
        compose_content = """
services:
  - web
  - db
"""
        is_valid, error = validate_docker_compose(compose_content)
        assert is_valid is False
        assert error is not None
        assert "'services' must be a dictionary" in error
    
    def test_empty_services(self):
        """Test validation fails when services section is empty"""
        compose_content = """
version: '3.8'
services: {}
"""
        is_valid, error = validate_docker_compose(compose_content)
        assert is_valid is False
        assert error is not None
        assert "'services' section cannot be empty" in error


class TestIsValidCompose:
    """Test is_valid_compose function"""
    
    def test_valid_compose_returns_true(self):
        """Test is_valid_compose returns True for valid content"""
        compose_content = """
services:
  web:
    image: nginx
"""
        assert is_valid_compose(compose_content) is True
    
    def test_invalid_compose_returns_false(self):
        """Test is_valid_compose returns False for invalid content"""
        assert is_valid_compose("") is False
    
    def test_raise_exception_on_invalid(self):
        """Test is_valid_compose raises exception when requested"""
        with pytest.raises(InvalidComposeError) as exc_info:
            is_valid_compose("", raise_exception=True)
        
        assert "cannot be empty" in str(exc_info.value)
    
    def test_no_exception_when_valid(self):
        """Test is_valid_compose doesn't raise exception for valid content"""
        compose_content = """
services:
  web:
    image: nginx
"""
        # Should not raise
        result = is_valid_compose(compose_content, raise_exception=True)
        assert result is True

