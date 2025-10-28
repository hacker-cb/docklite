"""Tests for response utilities"""
import pytest
from fastapi.responses import JSONResponse
from app.utils.responses import success_response, error_response, paginated_response


class TestSuccessResponse:
    """Test success_response function"""
    
    def test_basic_success_response(self):
        """Test creating basic success response"""
        result = success_response(data={"id": 1, "name": "test"})
        
        assert result["success"] is True
        assert result["data"] == {"id": 1, "name": "test"}
        assert "message" not in result
    
    def test_success_response_with_message(self):
        """Test success response with message"""
        result = success_response(
            data={"id": 1},
            message="Operation successful"
        )
        
        assert result["success"] is True
        assert result["data"] == {"id": 1}
        assert result["message"] == "Operation successful"
    
    def test_success_response_without_data(self):
        """Test success response without data"""
        result = success_response(message="Success")
        
        assert result["success"] is True
        assert result["data"] is None
        assert result["message"] == "Success"


class TestErrorResponse:
    """Test error_response function"""
    
    def test_basic_error_response(self):
        """Test creating basic error response"""
        result = error_response("Something went wrong")
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == 400
        content = result.body.decode()
        assert "Something went wrong" in content
        assert '"success":false' in content.lower() or '"success": false' in content.lower()
    
    def test_error_response_with_status_code(self):
        """Test error response with custom status code"""
        result = error_response("Not found", status_code=404)
        
        assert result.status_code == 404
    
    def test_error_response_with_details(self):
        """Test error response with additional details"""
        result = error_response(
            "Validation failed",
            status_code=422,
            details={"field": "email", "error": "Invalid format"}
        )
        
        assert result.status_code == 422
        content = result.body.decode()
        assert "Validation failed" in content
        assert "field" in content
        assert "email" in content


class TestPaginatedResponse:
    """Test paginated_response function"""
    
    def test_first_page(self):
        """Test paginated response for first page"""
        items = [{"id": i} for i in range(1, 11)]
        result = paginated_response(items, total=50, page=1, page_size=10)
        
        assert result["success"] is True
        assert len(result["data"]["items"]) == 10
        assert result["data"]["pagination"]["total"] == 50
        assert result["data"]["pagination"]["page"] == 1
        assert result["data"]["pagination"]["page_size"] == 10
        assert result["data"]["pagination"]["total_pages"] == 5
        assert result["data"]["pagination"]["has_next"] is True
        assert result["data"]["pagination"]["has_prev"] is False
    
    def test_middle_page(self):
        """Test paginated response for middle page"""
        items = [{"id": i} for i in range(11, 21)]
        result = paginated_response(items, total=50, page=2, page_size=10)
        
        assert result["data"]["pagination"]["page"] == 2
        assert result["data"]["pagination"]["has_next"] is True
        assert result["data"]["pagination"]["has_prev"] is True
    
    def test_last_page(self):
        """Test paginated response for last page"""
        items = [{"id": i} for i in range(41, 51)]
        result = paginated_response(items, total=50, page=5, page_size=10)
        
        assert result["data"]["pagination"]["page"] == 5
        assert result["data"]["pagination"]["total_pages"] == 5
        assert result["data"]["pagination"]["has_next"] is False
        assert result["data"]["pagination"]["has_prev"] is True
    
    def test_partial_last_page(self):
        """Test paginated response with partial last page"""
        items = [{"id": i} for i in range(1, 4)]
        result = paginated_response(items, total=23, page=3, page_size=10)
        
        assert len(result["data"]["items"]) == 3
        assert result["data"]["pagination"]["total"] == 23
        assert result["data"]["pagination"]["total_pages"] == 3
    
    def test_empty_page(self):
        """Test paginated response with no items"""
        result = paginated_response([], total=0, page=1, page_size=10)
        
        assert len(result["data"]["items"]) == 0
        assert result["data"]["pagination"]["total"] == 0
        assert result["data"]["pagination"]["total_pages"] == 0
        assert result["data"]["pagination"]["has_next"] is False
        assert result["data"]["pagination"]["has_prev"] is False

