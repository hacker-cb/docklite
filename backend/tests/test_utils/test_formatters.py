"""Tests for formatters utilities"""
import pytest
import json
from datetime import datetime
from app.utils.formatters import (
    format_project_response,
    format_user_response,
    safe_json_loads,
    safe_json_dumps
)


class TestFormatProjectResponse:
    """Test format_project_response function"""
    
    def test_format_project_with_env_vars(self):
        """Test formatting project with environment variables"""
        # Create mock project object
        class MockProject:
            id = 1
            name = "test-project"
            domain = "example.com"
            compose_content = "version: '3.8'\nservices:\n  web:\n    image: nginx"
            env_vars = '{"KEY": "value", "DB_HOST": "localhost"}'
            status = "running"
            created_at = datetime(2024, 1, 1, 12, 0, 0)
            updated_at = datetime(2024, 1, 2, 13, 30, 0)
        
        project = MockProject()
        result = format_project_response(project)
        
        assert result["id"] == 1
        assert result["name"] == "test-project"
        assert result["domain"] == "example.com"
        assert result["compose_content"] == project.compose_content
        assert result["env_vars"] == {"KEY": "value", "DB_HOST": "localhost"}
        assert result["status"] == "running"
        assert result["created_at"] == project.created_at
        assert result["updated_at"] == project.updated_at
    
    def test_format_project_with_empty_env_vars(self):
        """Test formatting project with empty environment variables"""
        class MockProject:
            id = 2
            name = "minimal-project"
            domain = "test.com"
            compose_content = "services:\n  app:\n    image: alpine"
            env_vars = None
            status = "created"
            created_at = datetime.now()
            updated_at = datetime.now()
        
        project = MockProject()
        result = format_project_response(project)
        
        assert result["env_vars"] == {}


class TestFormatUserResponse:
    """Test format_user_response function"""
    
    def test_format_admin_user(self):
        """Test formatting admin user"""
        class MockUser:
            id = 1
            username = "admin"
            email = "admin@example.com"
            is_active = 1
            is_admin = 1
            created_at = datetime(2024, 1, 1, 10, 0, 0)
        
        user = MockUser()
        result = format_user_response(user)
        
        assert result["id"] == 1
        assert result["username"] == "admin"
        assert result["email"] == "admin@example.com"
        assert result["is_active"] is True
        assert result["is_admin"] is True
        assert result["created_at"] == user.created_at
    
    def test_format_regular_user(self):
        """Test formatting regular user"""
        class MockUser:
            id = 2
            username = "user"
            email = "user@example.com"
            is_active = 1
            is_admin = 0
            created_at = datetime(2024, 1, 2, 11, 0, 0)
        
        user = MockUser()
        result = format_user_response(user)
        
        assert result["is_active"] is True
        assert result["is_admin"] is False
    
    def test_format_inactive_user(self):
        """Test formatting inactive user"""
        class MockUser:
            id = 3
            username = "inactive"
            email = "inactive@example.com"
            is_active = 0
            is_admin = 0
            created_at = datetime.now()
        
        user = MockUser()
        result = format_user_response(user)
        
        assert result["is_active"] is False


class TestSafeJsonLoads:
    """Test safe_json_loads function"""
    
    def test_valid_json(self):
        """Test parsing valid JSON"""
        json_str = '{"key": "value", "number": 42}'
        result = safe_json_loads(json_str)
        assert result == {"key": "value", "number": 42}
    
    def test_invalid_json(self):
        """Test parsing invalid JSON returns default"""
        result = safe_json_loads("not valid json")
        assert result == {}
    
    def test_custom_default(self):
        """Test using custom default value"""
        result = safe_json_loads("invalid", default={"error": True})
        assert result == {"error": True}
    
    def test_none_input(self):
        """Test parsing None returns default"""
        result = safe_json_loads(None)
        assert result == {}
    
    def test_empty_string(self):
        """Test parsing empty string returns default"""
        result = safe_json_loads("")
        assert result == {}


class TestSafeJsonDumps:
    """Test safe_json_dumps function"""
    
    def test_valid_object(self):
        """Test serializing valid object"""
        obj = {"key": "value", "number": 42}
        result = safe_json_dumps(obj)
        assert result == '{"key": "value", "number": 42}'
    
    def test_list_object(self):
        """Test serializing list"""
        obj = [1, 2, 3, "test"]
        result = safe_json_dumps(obj)
        assert result == '[1, 2, 3, "test"]'
    
    def test_non_serializable(self):
        """Test serializing non-serializable object returns default"""
        class CustomClass:
            pass
        
        obj = CustomClass()
        result = safe_json_dumps(obj)
        assert result == "{}"
    
    def test_custom_default(self):
        """Test using custom default value"""
        class CustomClass:
            pass
        
        obj = CustomClass()
        result = safe_json_dumps(obj, default="[]")
        assert result == "[]"

