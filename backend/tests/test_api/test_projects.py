import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestProjectsCRUD:
    """Tests for Projects CRUD API endpoints"""
    
    async def test_create_project_success(self, client: AsyncClient, sample_project_data, temp_projects_dir):
        """Test successful project creation"""
        response = await client.post("/api/projects", json=sample_project_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == sample_project_data["name"]
        assert data["domain"] == sample_project_data["domain"]
        assert data["compose_content"] == sample_project_data["compose_content"]
        assert data["status"] == "created"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # Verify port field is NOT in response
        assert "port" not in data or data["port"] is None
    
    async def test_create_project_without_port(self, client: AsyncClient, sample_compose_content, temp_projects_dir):
        """Test that port field is not required"""
        project_data = {
            "name": "test-no-port",
            "domain": "noport.local",
            "compose_content": sample_compose_content
        }
        
        response = await client.post("/api/projects", json=project_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "port" not in data or data["port"] is None
    
    async def test_create_project_duplicate_domain(self, client: AsyncClient, sample_project_data, temp_projects_dir):
        """Test that duplicate domain is rejected"""
        # Create first project
        await client.post("/api/projects", json=sample_project_data)
        
        # Try to create second with same domain
        response = await client.post("/api/projects", json=sample_project_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    async def test_create_project_invalid_compose(self, client: AsyncClient, invalid_compose_content, temp_projects_dir):
        """Test that invalid docker-compose.yml is rejected"""
        project_data = {
            "name": "invalid-project",
            "domain": "invalid.local",
            "compose_content": invalid_compose_content
        }
        
        response = await client.post("/api/projects", json=project_data)
        
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()
    
    async def test_create_project_missing_required_fields(self, client: AsyncClient, temp_projects_dir):
        """Test that missing required fields are rejected"""
        # Missing compose_content
        response = await client.post("/api/projects", json={
            "name": "test",
            "domain": "test.local"
        })
        assert response.status_code == 422
        
        # Missing domain
        response = await client.post("/api/projects", json={
            "name": "test",
            "compose_content": "version: '3.8'\nservices:\n  web:\n    image: nginx"
        })
        assert response.status_code == 422
        
        # Missing name
        response = await client.post("/api/projects", json={
            "domain": "test.local",
            "compose_content": "version: '3.8'\nservices:\n  web:\n    image: nginx"
        })
        assert response.status_code == 422
    
    async def test_get_projects_list(self, client: AsyncClient, sample_project_data, temp_projects_dir):
        """Test getting list of projects"""
        # Create a project
        await client.post("/api/projects", json=sample_project_data)
        
        # Get list
        response = await client.get("/api/projects")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "projects" in data
        assert "total" in data
        assert data["total"] >= 1
        assert len(data["projects"]) >= 1
        
        project = data["projects"][0]
        assert "id" in project
        assert "name" in project
        assert "domain" in project
        assert "status" in project
        # Port should not be in response or be null
        assert "port" not in project or project["port"] is None
    
    async def test_get_project_by_id(self, client: AsyncClient, sample_project_data, temp_projects_dir):
        """Test getting single project by ID"""
        # Create project
        create_response = await client.post("/api/projects", json=sample_project_data)
        project_id = create_response.json()["id"]
        
        # Get by ID
        response = await client.get(f"/api/projects/{project_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == project_id
        assert data["name"] == sample_project_data["name"]
        assert data["domain"] == sample_project_data["domain"]
    
    async def test_get_project_not_found(self, client: AsyncClient):
        """Test getting non-existent project returns 404"""
        response = await client.get("/api/projects/99999")
        
        assert response.status_code == 404
    
    async def test_update_project(self, client: AsyncClient, sample_project_data, temp_projects_dir):
        """Test updating project"""
        # Create project
        create_response = await client.post("/api/projects", json=sample_project_data)
        project_id = create_response.json()["id"]
        
        # Update
        update_data = {
            "name": "updated-name",
            "compose_content": "version: '3.8'\nservices:\n  app:\n    image: alpine"
        }
        
        response = await client.put(f"/api/projects/{project_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "updated-name"
        assert "alpine" in data["compose_content"]
    
    async def test_update_project_duplicate_domain(self, client: AsyncClient, sample_project_data, sample_compose_content, temp_projects_dir):
        """Test that updating to duplicate domain is rejected"""
        # Create two projects
        project1_response = await client.post("/api/projects", json=sample_project_data)
        project1_id = project1_response.json()["id"]
        
        project2_data = {
            "name": "project2",
            "domain": "project2.local",
            "compose_content": sample_compose_content
        }
        await client.post("/api/projects", json=project2_data)
        
        # Try to update project1 with project2's domain
        update_data = {"domain": "project2.local"}
        response = await client.put(f"/api/projects/{project1_id}", json=update_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    async def test_delete_project(self, client: AsyncClient, sample_project_data, temp_projects_dir):
        """Test deleting project"""
        # Create project
        create_response = await client.post("/api/projects", json=sample_project_data)
        project_id = create_response.json()["id"]
        
        # Delete
        response = await client.delete(f"/api/projects/{project_id}")
        
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = await client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 404
    
    async def test_delete_project_not_found(self, client: AsyncClient):
        """Test deleting non-existent project returns 404"""
        response = await client.delete("/api/projects/99999")
        
        assert response.status_code == 404

