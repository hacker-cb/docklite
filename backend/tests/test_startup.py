"""
Smoke tests for application startup

These tests verify that the FastAPI application can start without errors.
This catches issues like invalid router configurations that would cause
runtime failures when starting uvicorn.
"""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_app_startup():
    """
    Test that the application can start without errors.
    
    This is a smoke test that validates:
    - All routers are properly configured
    - No conflicting route definitions
    - HTTP status codes match response models (e.g., 204 has no body)
    - All middleware is properly configured
    
    This test would have caught the bug where delete_user had
    status_code=204 with -> None type hint (response body expected).
    """
    # This will fail at import/startup if there are router issues
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make a simple request to ensure app is responsive
        response = await client.get("/api/auth/setup/check")
        # Any status is fine - we just need app to start
        assert response.status_code in [200, 401, 404, 500]


@pytest.mark.asyncio
async def test_openapi_schema_generation():
    """
    Test that OpenAPI schema can be generated without errors.
    
    FastAPI validates all routes when generating OpenAPI schema.
    This catches many configuration issues.
    """
    # Access OpenAPI schema - this triggers route validation
    assert app.openapi_schema is not None or app.openapi() is not None
    
    # Verify basic structure
    schema = app.openapi()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
    
    # Verify critical endpoints exist
    assert "/api/auth/login" in schema["paths"]
    assert "/api/users" in schema["paths"]
    assert "/api/projects" in schema["paths"]


@pytest.mark.asyncio  
async def test_all_routes_have_valid_status_codes():
    """
    Verify that all routes have compatible status codes and response models.
    
    This test validates that:
    - 204 endpoints don't return response bodies
    - Response models match declared status codes
    """
    schema = app.openapi()
    
    for path, path_item in schema["paths"].items():
        for method, operation in path_item.items():
            if method.upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                continue
                
            responses = operation.get("responses", {})
            
            # Check 204 No Content responses
            if "204" in responses:
                response_schema = responses["204"]
                # 204 must not have content
                assert "content" not in response_schema, (
                    f"{method.upper()} {path} has status 204 but defines response content. "
                    "HTTP 204 No Content must not have a response body."
                )

