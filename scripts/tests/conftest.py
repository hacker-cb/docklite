"""Pytest configuration and fixtures for CLI tests."""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
import subprocess


@pytest.fixture
def project_root():
    """Get project root path (auto-detected)."""
    # Auto-detect from script location
    return Path(__file__).parent.parent.parent.absolute()


@pytest.fixture
def mock_docker_compose():
    """Mock docker_compose_cmd function."""
    mock = Mock()
    mock.return_value = Mock(
        stdout="",
        stderr="",
        returncode=0
    )
    return mock


@pytest.fixture
def mock_container_running():
    """Mock is_container_running function."""
    return Mock(return_value=True)


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run."""
    mock = Mock()
    mock.return_value = Mock(
        stdout="",
        stderr="",
        returncode=0
    )
    return mock

