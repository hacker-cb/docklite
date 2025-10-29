"""Tests for console utilities."""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.utils.console import (
    log_info,
    log_success,
    log_error,
    log_warning,
    log_step,
    print_banner,
    create_table,
    create_progress
)


class TestLogging:
    """Tests for logging functions."""
    
    def test_log_info(self, capsys):
        """Test log_info outputs message."""
        log_info("Test message")
        # Just verify it doesn't raise an error
    
    def test_log_success(self, capsys):
        """Test log_success outputs message."""
        log_success("Success message")
        # Just verify it doesn't raise an error
    
    def test_log_error(self):
        """Test log_error outputs to stderr."""
        # Just verify it doesn't raise an error
        log_error("Error message")
    
    def test_log_warning(self):
        """Test log_warning outputs message."""
        log_warning("Warning message")
    
    def test_log_step(self):
        """Test log_step outputs message."""
        log_step("Step message")


class TestPrintBanner:
    """Tests for print_banner function."""
    
    def test_print_banner_with_title(self):
        """Test print_banner prints title."""
        print_banner("Test Title")
        # Just verify it doesn't raise an error


class TestCreateTable:
    """Tests for create_table function."""
    
    def test_create_table_returns_table(self):
        """Test create_table returns Table object."""
        from rich.table import Table
        table = create_table("Test Table")
        assert isinstance(table, Table)
    
    def test_create_table_with_title(self):
        """Test create_table with title."""
        table = create_table("My Title")
        assert table.title == "My Title"
    
    def test_create_table_default_options(self):
        """Test create_table with default options."""
        table = create_table()
        assert table is not None


class TestCreateProgress:
    """Tests for create_progress function."""
    
    def test_create_progress_returns_progress(self):
        """Test create_progress returns Progress object."""
        from rich.progress import Progress
        progress = create_progress()
        assert isinstance(progress, Progress)

