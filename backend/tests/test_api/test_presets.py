import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestPresets:
    """Tests for Presets API endpoints"""
    
    async def test_get_all_presets(self, client: AsyncClient):
        """Test getting all presets"""
        response = await client.get("/api/presets")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0  # Should have at least some presets
        
        # Check structure of first preset
        if data:
            preset = data[0]
            assert "id" in preset
            assert "name" in preset
            assert "description" in preset
            assert "category" in preset
            assert "icon" in preset
            assert "tags" in preset
            
            # Verify default_port is NOT in response
            assert "default_port" not in preset
    
    async def test_get_presets_by_category(self, client: AsyncClient):
        """Test filtering presets by category"""
        response = await client.get("/api/presets?category=web")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # All returned presets should be in 'web' category
        for preset in data:
            assert preset["category"] == "web"
    
    async def test_get_presets_categories(self, client: AsyncClient):
        """Test getting categories list"""
        response = await client.get("/api/presets/categories")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 4  # At least 4 categories (+ "all")
        
        # Check structure
        category_ids = [cat["id"] for cat in data]
        assert "all" in category_ids
        assert "web" in category_ids
        assert "backend" in category_ids
        assert "database" in category_ids
        assert "cms" in category_ids
        
        # Each category should have count
        for cat in data:
            assert "id" in cat
            assert "name" in cat
            assert "count" in cat
            assert isinstance(cat["count"], int)
            assert cat["count"] >= 0
    
    async def test_get_preset_by_id(self, client: AsyncClient):
        """Test getting single preset by ID"""
        # Use nginx-static as it should always exist
        response = await client.get("/api/presets/nginx-static")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == "nginx-static"
        assert data["name"]
        assert data["description"]
        assert data["category"] == "web"
        assert data["icon"]
        assert "compose_content" in data
        assert "default_env_vars" in data
        assert isinstance(data["default_env_vars"], dict)
        assert "tags" in data
        
        # Verify default_port is NOT in response
        assert "default_port" not in data
        
        # Verify compose_content is not empty
        assert len(data["compose_content"]) > 0
        assert "version:" in data["compose_content"] or "services:" in data["compose_content"]
    
    async def test_get_preset_not_found(self, client: AsyncClient):
        """Test getting non-existent preset returns 404"""
        response = await client.get("/api/presets/non-existent-preset")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_presets_structure(self, client: AsyncClient):
        """Test that all presets have required fields"""
        response = await client.get("/api/presets")
        data = response.json()
        
        required_fields = ["id", "name", "description", "category", "icon", "tags"]
        
        for preset in data:
            for field in required_fields:
                assert field in preset, f"Preset {preset.get('id')} missing field: {field}"
            
            # Verify types
            assert isinstance(preset["id"], str)
            assert isinstance(preset["name"], str)
            assert isinstance(preset["description"], str)
            assert isinstance(preset["category"], str)
            assert isinstance(preset["icon"], str)
            assert isinstance(preset["tags"], list)
            
            # Verify category is valid
            assert preset["category"] in ["web", "backend", "database", "cms", "examples"]

