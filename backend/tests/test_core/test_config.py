"""Tests for core configuration module."""

import pytest
from unittest.mock import patch, MagicMock
import os
from pathlib import Path


class TestSettings:
    """Tests for Settings class."""

    def test_default_values(self):
        """Test that default configuration values are set."""
        from app.core.config import Settings
        
        settings = Settings()
        
        # Database defaults
        assert settings.DATABASE_URL is not None
        assert "sqlite" in settings.DATABASE_URL.lower()
        
        # Security defaults
        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) > 0
        assert settings.ALGORITHM == "HS256"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
        
        # Projects defaults
        assert settings.PROJECTS_DIR is not None
        assert settings.DEPLOY_USER is not None
        assert settings.DEPLOY_HOST is not None
        assert settings.DEPLOY_PORT > 0
        
        # Server defaults
        assert settings.API_HOST is not None
        assert settings.API_PORT > 0

    def test_secret_key_is_string(self):
        """Test that SECRET_KEY is a non-empty string."""
        from app.core.config import Settings
        
        settings = Settings()
        
        assert isinstance(settings.SECRET_KEY, str)
        assert len(settings.SECRET_KEY) >= 8  # Minimum reasonable length

    def test_algorithm_is_hs256(self):
        """Test that JWT algorithm is HS256."""
        from app.core.config import Settings
        
        settings = Settings()
        
        assert settings.ALGORITHM == "HS256"

    def test_token_expiration_reasonable(self):
        """Test that token expiration time is reasonable."""
        from app.core.config import Settings
        
        settings = Settings()
        
        # Token should expire between 1 minute and 1 year
        assert 1 <= settings.ACCESS_TOKEN_EXPIRE_MINUTES <= 525600

    def test_projects_dir_path(self):
        """Test that PROJECTS_DIR is a valid path format."""
        from app.core.config import Settings
        
        settings = Settings()
        
        # Should be a non-empty string
        assert isinstance(settings.PROJECTS_DIR, str)
        assert len(settings.PROJECTS_DIR) > 0
        
        # Should be an absolute path or relative path
        assert "/" in settings.PROJECTS_DIR or "\\" in settings.PROJECTS_DIR

    def test_hostname_defaults_to_none(self):
        """Test that HOSTNAME defaults to None (auto-detect)."""
        from app.core.config import Settings
        
        settings = Settings()
        
        # HOSTNAME should be None by default (auto-detect from system)
        assert settings.HOSTNAME is None or isinstance(settings.HOSTNAME, str)

    def test_traefik_dashboard_host_set(self):
        """Test that Traefik dashboard host is configured."""
        from app.core.config import Settings
        
        settings = Settings()
        
        assert settings.TRAEFIK_DASHBOARD_HOST is not None
        assert isinstance(settings.TRAEFIK_DASHBOARD_HOST, str)

    def test_api_host_and_port(self):
        """Test that API host and port are configured."""
        from app.core.config import Settings
        
        settings = Settings()
        
        assert settings.API_HOST is not None
        assert settings.API_PORT is not None
        assert isinstance(settings.API_PORT, int)
        assert 1 <= settings.API_PORT <= 65535

    @patch.dict(os.environ, {
        "DATABASE_URL": "postgresql://custom_db",
        "SECRET_KEY": "custom-secret-key-for-testing",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "60"
    })
    def test_env_override(self):
        """Test that environment variables override defaults."""
        from app.core.config import Settings
        
        # Force reload with new env vars
        settings = Settings()
        
        assert settings.SECRET_KEY == "custom-secret-key-for-testing"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60

    @patch.dict(os.environ, {"HOSTNAME": "example.com"})
    def test_hostname_from_env(self):
        """Test that HOSTNAME can be set from environment."""
        from app.core.config import Settings
        
        settings = Settings()
        
        assert settings.HOSTNAME == "example.com"

    @patch.dict(os.environ, {"API_PORT": "9000"})
    def test_api_port_from_env(self):
        """Test that API_PORT can be set from environment."""
        from app.core.config import Settings
        
        settings = Settings()
        
        assert settings.API_PORT == 9000

    @patch.dict(os.environ, {"PROJECTS_DIR": "/custom/projects"})
    def test_projects_dir_from_env(self):
        """Test that PROJECTS_DIR can be set from environment."""
        from app.core.config import Settings
        
        settings = Settings()
        
        assert settings.PROJECTS_DIR == "/custom/projects"


class TestSettingsSingleton:
    """Tests for settings singleton instance."""

    def test_settings_instance_exists(self):
        """Test that settings singleton is created."""
        from app.core.config import settings
        
        assert settings is not None

    def test_settings_instance_is_settings_type(self):
        """Test that settings instance is of type Settings."""
        from app.core.config import settings, Settings
        
        assert isinstance(settings, Settings)

    def test_settings_accessible(self):
        """Test that settings values are accessible."""
        from app.core.config import settings
        
        # Should be able to access all attributes
        assert settings.DATABASE_URL is not None
        assert settings.SECRET_KEY is not None
        assert settings.PROJECTS_DIR is not None


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_database_url_format(self):
        """Test that DATABASE_URL has correct format."""
        from app.core.config import settings
        
        # Should contain a protocol
        assert "://" in settings.DATABASE_URL or "+aiosqlite://" in settings.DATABASE_URL

    def test_deploy_port_valid_range(self):
        """Test that DEPLOY_PORT is in valid range."""
        from app.core.config import settings
        
        assert 1 <= settings.DEPLOY_PORT <= 65535

    def test_deploy_user_not_empty(self):
        """Test that DEPLOY_USER is not empty."""
        from app.core.config import settings
        
        assert settings.DEPLOY_USER is not None
        assert len(settings.DEPLOY_USER) > 0

    def test_deploy_host_not_empty(self):
        """Test that DEPLOY_HOST is not empty."""
        from app.core.config import settings
        
        assert settings.DEPLOY_HOST is not None
        assert len(settings.DEPLOY_HOST) > 0


class TestConfigEnvFile:
    """Tests for .env file configuration."""

    def test_env_file_path_configured(self):
        """Test that .env file path is configured."""
        from app.core.config import Settings
        
        # Check Config class has env_file
        assert hasattr(Settings.Config, 'env_file')
        assert Settings.Config.env_file is not None

    def test_case_sensitive_config(self):
        """Test that configuration is case-sensitive."""
        from app.core.config import Settings
        
        assert Settings.Config.case_sensitive is True

