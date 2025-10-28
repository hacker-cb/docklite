import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthSetup:
    """Tests for initial setup endpoints"""
    
    async def test_setup_check_empty_db(self, client: AsyncClient):
        """Test setup check with empty database"""
        response = await client.get("/api/auth/setup/check")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "setup_needed" in data
        assert "has_users" in data
        assert data["setup_needed"] is True
        assert data["has_users"] is False
    
    async def test_setup_create_first_admin(self, client: AsyncClient, temp_projects_dir):
        """Test creating first admin user through setup"""
        user_data = {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123"
        }
        
        response = await client.post("/api/auth/setup", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    async def test_setup_check_with_users(self, client: AsyncClient, temp_projects_dir):
        """Test setup check after user is created"""
        # Create first user
        user_data = {
            "username": "admin",
            "password": "admin123"
        }
        await client.post("/api/auth/setup", json=user_data)
        
        # Check setup status
        response = await client.get("/api/auth/setup/check")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["setup_needed"] is False
        assert data["has_users"] is True
    
    async def test_setup_fails_when_users_exist(self, client: AsyncClient, temp_projects_dir):
        """Test that setup fails when users already exist"""
        # Create first user
        user_data = {
            "username": "admin",
            "password": "admin123"
        }
        await client.post("/api/auth/setup", json=user_data)
        
        # Try to create another through setup
        second_user = {
            "username": "admin2",
            "password": "admin123"
        }
        response = await client.post("/api/auth/setup", json=second_user)
        
        assert response.status_code == 400
        assert "already exist" in response.json()["detail"].lower()


@pytest.mark.asyncio
class TestAuthLogin:
    """Tests for login endpoint"""
    
    async def test_login_success(self, client: AsyncClient, temp_projects_dir):
        """Test successful login"""
        # Create user first
        await client.post("/api/auth/setup", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        # Login
        response = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_wrong_password(self, client: AsyncClient, temp_projects_dir):
        """Test login with wrong password"""
        # Create user
        await client.post("/api/auth/setup", json={
            "username": "testuser",
            "password": "correctpass"
        })
        
        # Try login with wrong password
        response = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "wrongpass"
        })
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent username"""
        response = await client.post("/api/auth/login", json={
            "username": "nonexistent",
            "password": "somepass"
        })
        
        assert response.status_code == 401


@pytest.mark.asyncio
class TestAuthMe:
    """Tests for /me endpoint"""
    
    async def test_get_current_user_with_token(self, client: AsyncClient, temp_projects_dir):
        """Test getting current user info with valid token"""
        # Create and login
        login_response = await client.post("/api/auth/setup", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        })
        token = login_response.json()["access_token"]
        
        # Get user info
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["is_active"] is True
        assert data["is_admin"] is True  # First user is admin
        assert "id" in data
        assert "created_at" in data
    
    async def test_get_current_user_without_token(self, client: AsyncClient):
        """Test that /me endpoint requires authentication"""
        response = await client.get("/api/auth/me")
        
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
    
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test /me endpoint with invalid token"""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token-12345"}
        )
        
        assert response.status_code == 401


@pytest.mark.asyncio
class TestAuthLogout:
    """Tests for logout endpoint"""
    
    async def test_logout_with_token(self, client: AsyncClient, temp_projects_dir):
        """Test logout with valid token"""
        # Create and login
        login_response = await client.post("/api/auth/setup", json={
            "username": "testuser",
            "password": "testpass123"
        })
        token = login_response.json()["access_token"]
        
        # Logout
        response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "successfully" in response.json()["message"].lower()
    
    async def test_logout_without_token(self, client: AsyncClient):
        """Test that logout requires authentication"""
        response = await client.post("/api/auth/logout")
        
        assert response.status_code == 403

