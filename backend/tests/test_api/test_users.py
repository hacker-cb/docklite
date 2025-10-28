import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUsersAPI:
    """Tests for Users Management API endpoints"""
    
    async def test_get_users_as_admin(self, client: AsyncClient, auth_token):
        """Test getting users list as admin"""
        response = await client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the test admin
        
        # Check structure
        user = data[0]
        assert "id" in user
        assert "username" in user
        assert "email" in user
        assert "is_active" in user
        assert "is_admin" in user
        assert "created_at" in user
        assert "password_hash" not in user  # Should not expose password
    
    async def test_create_user_as_admin(self, client: AsyncClient, auth_token, temp_projects_dir):
        """Test creating user as admin"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123"
        }
        
        response = await client.post(
            "/api/users",
            json=user_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["is_active"] is True
        assert data["is_admin"] is False  # New users are not admin by default
    
    async def test_create_user_duplicate_username(self, client: AsyncClient, auth_token, temp_projects_dir):
        """Test creating user with duplicate username"""
        user_data = {
            "username": "testadmin",  # Already exists from auth_token fixture
            "password": "pass123"
        }
        
        response = await client.post(
            "/api/users",
            json=user_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    async def test_get_user_by_id(self, client: AsyncClient, auth_token, temp_projects_dir):
        """Test getting user by ID"""
        # Create a user first
        create_response = await client.post(
            "/api/users",
            json={"username": "testuser", "password": "pass123"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        user_id = create_response.json()["id"]
        
        # Get by ID
        response = await client.get(
            f"/api/users/{user_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
    
    async def test_update_user_active_status(self, client: AsyncClient, auth_token, temp_projects_dir):
        """Test updating user active status"""
        # Create a user
        create_response = await client.post(
            "/api/users",
            json={"username": "testuser", "password": "pass123"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        user_id = create_response.json()["id"]
        
        # Deactivate user
        response = await client.put(
            f"/api/users/{user_id}?is_active=false",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
    
    async def test_update_user_admin_status(self, client: AsyncClient, auth_token, temp_projects_dir):
        """Test updating user admin status"""
        # Create a user
        create_response = await client.post(
            "/api/users",
            json={"username": "testuser", "password": "pass123"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        user_id = create_response.json()["id"]
        
        # Make admin
        response = await client.put(
            f"/api/users/{user_id}?is_admin=true",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_admin"] is True
    
    async def test_cannot_modify_own_account(self, client: AsyncClient, auth_token, db_session):
        """Test that admin cannot modify their own account"""
        from app.models.user import User
        from sqlalchemy import select
        
        # Get admin user ID
        result = await db_session.execute(select(User).where(User.username == "testadmin"))
        admin = result.scalar_one()
        
        # Try to deactivate self
        response = await client.put(
            f"/api/users/{admin.id}?is_active=false",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
        assert "cannot modify your own" in response.json()["detail"].lower()
    
    async def test_delete_user(self, client: AsyncClient, auth_token, temp_projects_dir):
        """Test deleting user"""
        # Create a user
        create_response = await client.post(
            "/api/users",
            json={"username": "testuser", "password": "pass123"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        user_id = create_response.json()["id"]
        
        # Delete
        response = await client.delete(
            f"/api/users/{user_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 204
        
        # Verify deleted
        get_response = await client.get(
            f"/api/users/{user_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert get_response.status_code == 404
    
    async def test_cannot_delete_own_account(self, client: AsyncClient, auth_token, db_session):
        """Test that admin cannot delete their own account"""
        from app.models.user import User
        from sqlalchemy import select
        
        # Get admin user ID
        result = await db_session.execute(select(User).where(User.username == "testadmin"))
        admin = result.scalar_one()
        
        # Try to delete self
        response = await client.delete(
            f"/api/users/{admin.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
        assert "cannot delete your own" in response.json()["detail"].lower()
    
    async def test_change_password(self, client: AsyncClient, auth_token, temp_projects_dir):
        """Test changing user password"""
        # Create a user
        create_response = await client.post(
            "/api/users",
            json={"username": "testuser", "password": "oldpass123"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        user_id = create_response.json()["id"]
        
        # Change password
        response = await client.put(
            f"/api/users/{user_id}/password?new_password=newpass123",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        assert "successfully" in response.json()["message"].lower()
    
    async def test_change_password_too_short(self, client: AsyncClient, auth_token, temp_projects_dir):
        """Test changing password with too short password"""
        # Create a user
        create_response = await client.post(
            "/api/users",
            json={"username": "testuser", "password": "pass123"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        user_id = create_response.json()["id"]
        
        # Try to change to short password
        response = await client.put(
            f"/api/users/{user_id}/password?new_password=12345",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
        assert "at least 6" in response.json()["detail"].lower()

