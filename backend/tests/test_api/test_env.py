import pytest
from httpx import AsyncClient
from pathlib import Path


@pytest.mark.asyncio
class TestEnvironmentVariables:
    """Tests for environment variables API endpoints"""
    
    async def test_get_env_vars(self, client: AsyncClient, sample_project_data, temp_projects_dir, auth_token):
        """Test getting environment variables"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create project with env vars
        create_response = await client.post("/api/projects", json=sample_project_data, headers=headers)
        project_id = create_response.json()["id"]
        
        # Get env vars
        response = await client.get(f"/api/projects/{project_id}/env", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert data["ENV"] == "test"
        assert data["DEBUG"] == "true"
    
    async def test_get_env_vars_project_not_found(self, client: AsyncClient, auth_token):
        """Test getting env vars for non-existent project returns 404"""
        response = await client.get(
            "/api/projects/99999/env",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
    
    async def test_update_env_vars(self, client: AsyncClient, sample_project_data, temp_projects_dir, auth_token):
        """Test updating environment variables"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create project
        create_response = await client.post("/api/projects", json=sample_project_data, headers=headers)
        project_id = create_response.json()["id"]
        
        # Update env vars
        new_env_vars = {
            "API_KEY": "secret123",
            "DATABASE_URL": "postgresql://localhost/db",
            "PORT": "3000"
        }
        
        response = await client.put(f"/api/projects/{project_id}/env", json=new_env_vars, headers=headers)
        
        assert response.status_code == 200
        assert "updated successfully" in response.json()["message"].lower()
        
        # Verify updated
        get_response = await client.get(f"/api/projects/{project_id}/env", headers=headers)
        data = get_response.json()
        
        assert data["API_KEY"] == "secret123"
        assert data["DATABASE_URL"] == "postgresql://localhost/db"
        assert data["PORT"] == "3000"
    
    async def test_update_env_vars_creates_file(self, client: AsyncClient, sample_project_data, temp_projects_dir, auth_token):
        """Test that updating env vars creates .env file"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create project
        create_response = await client.post("/api/projects", json=sample_project_data, headers=headers)
        project_id = create_response.json()["id"]
        
        # Update env vars
        env_vars = {"KEY1": "value1", "KEY2": "value2"}
        await client.put(f"/api/projects/{project_id}/env", json=env_vars, headers=headers)
        
        # Check .env file exists
        env_file = Path(temp_projects_dir) / str(project_id) / ".env"
        assert env_file.exists()
        
        # Check content
        content = env_file.read_text()
        assert "KEY1=value1" in content
        assert "KEY2=value2" in content
    
    async def test_update_env_vars_empty(self, client: AsyncClient, sample_project_data, temp_projects_dir, auth_token):
        """Test updating with empty env vars"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create project
        create_response = await client.post("/api/projects", json=sample_project_data, headers=headers)
        project_id = create_response.json()["id"]
        
        # Update with empty dict
        response = await client.put(f"/api/projects/{project_id}/env", json={}, headers=headers)
        
        assert response.status_code == 200
        
        # Verify empty
        get_response = await client.get(f"/api/projects/{project_id}/env", headers=headers)
        assert get_response.json() == {}
    
    async def test_update_env_vars_project_not_found(self, client: AsyncClient, auth_token):
        """Test updating env vars for non-existent project returns 404"""
        response = await client.put(
            "/api/projects/99999/env",
            json={"KEY": "value"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
