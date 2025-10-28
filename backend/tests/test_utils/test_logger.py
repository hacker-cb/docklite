"""Tests for logger utilities"""
import pytest
import logging
from unittest.mock import Mock, MagicMock
from app.utils.logger import get_logger, log_request, log_error


class TestGetLogger:
    """Test get_logger function"""
    
    def test_get_logger_returns_logger(self):
        """Test get_logger returns a Logger instance"""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
    
    def test_logger_has_handler(self):
        """Test logger has at least one handler"""
        logger = get_logger("test_with_handler")
        assert len(logger.handlers) > 0
    
    def test_logger_has_formatter(self):
        """Test logger handler has formatter"""
        logger = get_logger("test_formatter")
        handler = logger.handlers[0]
        assert handler.formatter is not None
    
    def test_logger_level(self):
        """Test logger has correct level"""
        logger = get_logger("test_level")
        assert logger.level == logging.INFO


class TestLogRequest:
    """Test log_request function"""
    
    def test_log_request_with_logger(self):
        """Test logging request with provided logger"""
        mock_logger = Mock()
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url.path = "/api/projects"
        mock_request.client.host = "127.0.0.1"
        
        log_request(mock_request, logger=mock_logger)
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "GET" in call_args
        assert "/api/projects" in call_args
        assert "127.0.0.1" in call_args
    
    def test_log_request_without_logger(self):
        """Test logging request without logger (uses default)"""
        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.url.path = "/api/auth/login"
        mock_request.client.host = "192.168.1.1"
        
        # Should not raise exception
        log_request(mock_request)
    
    def test_log_request_without_client(self):
        """Test logging request without client info"""
        mock_logger = Mock()
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url.path = "/api/test"
        mock_request.client = None
        
        log_request(mock_request, logger=mock_logger)
        
        call_args = mock_logger.info.call_args[0][0]
        assert "Unknown" in call_args


class TestLogError:
    """Test log_error function"""
    
    def test_log_error_with_logger(self):
        """Test logging error with provided logger"""
        mock_logger = Mock()
        error = ValueError("Test error")
        
        log_error(error, logger=mock_logger)
        
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "Test error" in call_args
    
    def test_log_error_with_context(self):
        """Test logging error with context"""
        mock_logger = Mock()
        error = RuntimeError("Something failed")
        
        log_error(error, context="API call", logger=mock_logger)
        
        call_args = mock_logger.error.call_args[0][0]
        assert "API call" in call_args
        assert "Something failed" in call_args
    
    def test_log_error_without_logger(self):
        """Test logging error without logger (uses default)"""
        error = Exception("Test exception")
        
        # Should not raise exception
        log_error(error)
    
    def test_log_error_with_exc_info(self):
        """Test logging error includes exception info"""
        mock_logger = Mock()
        error = TypeError("Type mismatch")
        
        log_error(error, logger=mock_logger)
        
        # Check that exc_info=True was passed
        call_kwargs = mock_logger.error.call_args[1]
        assert call_kwargs.get("exc_info") is True

