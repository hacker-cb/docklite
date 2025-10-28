import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestProtectedEndpoints:
    """Tests for authentication on protected endpoints"""
    
    async def test_projects_list_without_token(self, client: AsyncClient):
        """Test that projects endpoint requires authentication"""
        response = await client.get("/api/projects")
        
        assert response.status_code == 403
    
    async def test_projects_list_with_token(self, client: AsyncClient, sample_compose_content, temp_projects_dir):
        """Test that projects endpoint works with valid token"""
        # Setup and get token
        login_response = await client.post("/api/auth/setup", json={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        # Access protected endpoint
        response = await client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "projects" in response.json()
    
    async def test_create_project_without_token(self, client: AsyncClient, sample_project_data):
        """Test that creating project requires authentication"""
        response = await client.post("/api/projects", json=sample_project_data)
        
        assert response.status_code == 403
    
    async def test_create_project_with_token(self, client: AsyncClient, sample_project_data, temp_projects_dir):
        """Test that creating project works with valid token"""
        # Setup and get token
        login_response = await client.post("/api/auth/setup", json={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        # Create project
        response = await client.post(
            "/api/projects",
            json=sample_project_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        assert "id" in response.json()
    
    async def test_public_endpoints_no_auth(self, client: AsyncClient):
        """Test that public endpoints work without authentication"""
        # Presets should be public
        presets_response = await client.get("/api/presets")
        assert presets_response.status_code == 200
        
        # Setup check should be public
        setup_response = await client.get("/api/auth/setup/check")
        assert setup_response.status_code == 200
        
        # Health check should be public
        health_response = await client.get("/health")
        assert health_response.status_code == 200
    
    async def test_invalid_token_format(self, client: AsyncClient):
        """Test that invalid token format is rejected"""
        response = await client.get(
            "/api/projects",
            headers={"Authorization": "Bearer not-a-real-jwt-token"}
        )
        
        assert response.status_code == 401
    
    async def test_missing_bearer_prefix(self, client: AsyncClient, temp_projects_dir):
        """Test that token without Bearer prefix is rejected"""
        # Get a valid token
        login_response = await client.post("/api/auth/setup", json={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        # Try to use it without Bearer prefix
        response = await client.get(
            "/api/projects",
            headers={"Authorization": token}  # Missing "Bearer "
        )
        
        assert response.status_code == 403

