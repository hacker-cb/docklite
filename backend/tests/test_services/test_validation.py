import pytest
from app.services.project_service import ProjectService
from unittest.mock import AsyncMock


@pytest.mark.asyncio
class TestDockerComposeValidation:
    """Tests for docker-compose.yml validation"""
    
    async def test_valid_compose_content(self, db_session):
        """Test that valid docker-compose.yml passes validation"""
        service = ProjectService(db_session)
        
        valid_compose = """version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
"""
        
        is_valid, error = await service.validate_compose_content(valid_compose)
        
        assert is_valid is True
        assert error is None
    
    async def test_valid_compose_without_version(self, db_session):
        """Test that compose without version but with services is valid"""
        service = ProjectService(db_session)
        
        valid_compose = """services:
  app:
    image: alpine
    command: echo "Hello"
"""
        
        is_valid, error = await service.validate_compose_content(valid_compose)
        
        assert is_valid is True
        assert error is None
    
    async def test_invalid_yaml_syntax(self, db_session):
        """Test that invalid YAML syntax is rejected"""
        service = ProjectService(db_session)
        
        invalid_compose = """this is not valid yaml: [[[
  broken: {{{
"""
        
        is_valid, error = await service.validate_compose_content(invalid_compose)
        
        assert is_valid is False
        assert error is not None
        assert "yaml" in error.lower() or "parsing" in error.lower()
    
    async def test_compose_without_services(self, db_session):
        """Test that compose without services section is rejected"""
        service = ProjectService(db_session)
        
        invalid_compose = """version: '3.8'
name: myapp
networks:
  default:
"""
        
        is_valid, error = await service.validate_compose_content(invalid_compose)
        
        assert is_valid is False
        assert error is not None
        assert "services" in error.lower()
    
    async def test_compose_with_invalid_services_type(self, db_session):
        """Test that services must be a dictionary"""
        service = ProjectService(db_session)
        
        invalid_compose = """version: '3.8'
services: just_a_string
"""
        
        is_valid, error = await service.validate_compose_content(invalid_compose)
        
        assert is_valid is False
        assert error is not None
        assert "services" in error.lower() or "dictionary" in error.lower()
    
    async def test_compose_not_dict(self, db_session):
        """Test that compose root must be a dictionary"""
        service = ProjectService(db_session)
        
        invalid_compose = """- just
- a
- list
"""
        
        is_valid, error = await service.validate_compose_content(invalid_compose)
        
        assert is_valid is False
        assert error is not None
    
    async def test_empty_compose(self, db_session):
        """Test that empty compose is rejected"""
        service = ProjectService(db_session)
        
        is_valid, error = await service.validate_compose_content("")
        
        assert is_valid is False
        assert error is not None
    
    async def test_compose_with_only_comments(self, db_session):
        """Test that compose with only comments is rejected"""
        service = ProjectService(db_session)
        
        invalid_compose = """# Just comments
# No actual content
"""
        
        is_valid, error = await service.validate_compose_content(invalid_compose)
        
        assert is_valid is False
        assert error is not None
    
    async def test_complex_valid_compose(self, db_session):
        """Test complex but valid docker-compose.yml"""
        service = ProjectService(db_session)
        
        complex_compose = """version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html
    environment:
      - NGINX_HOST=example.com
    depends_on:
      - app
    networks:
      - frontend
  
  app:
    build: ./app
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://db/myapp
    networks:
      - frontend
      - backend
  
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - backend

networks:
  frontend:
  backend:

volumes:
  db-data:
"""
        
        is_valid, error = await service.validate_compose_content(complex_compose)
        
        assert is_valid is True
        assert error is None

