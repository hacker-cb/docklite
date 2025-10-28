import pytest
from app.validators import validate_docker_compose
from unittest.mock import AsyncMock


@pytest.mark.asyncio
class TestDockerComposeValidation:
    """Tests for docker-compose.yml validation"""
    
    async def test_valid_compose_content(self):
        """Test that valid docker-compose.yml passes validation"""
        valid_compose = """version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
"""
        
        is_valid, error = validate_docker_compose(valid_compose)
        
        assert is_valid is True
        assert error is None
    
    async def test_valid_compose_without_version(self):
        """Test that compose without version but with services is valid"""
        valid_compose = """services:
  app:
    image: alpine
    command: echo "Hello"
"""
        
        is_valid, error = validate_docker_compose(valid_compose)
        
        assert is_valid is True
        assert error is None
    
    async def test_invalid_yaml_syntax(self):
        """Test that invalid YAML syntax is rejected"""
        invalid_compose = """this is not valid yaml: [[[
  broken: {{{
"""
        
        is_valid, error = validate_docker_compose(invalid_compose)
        
        assert is_valid is False
        assert error is not None
        assert "yaml" in error.lower() or "parsing" in error.lower()
    
    async def test_compose_without_services(self):
        """Test that compose without services section is rejected"""
        invalid_compose = """version: '3.8'
name: myapp
networks:
  default:
"""
        
        is_valid, error = validate_docker_compose(invalid_compose)
        
        assert is_valid is False
        assert error is not None
        assert "services" in error.lower()
    
    async def test_compose_with_invalid_services_type(self):
        """Test that services must be a dictionary"""
        invalid_compose = """version: '3.8'
services: just_a_string
"""
        
        is_valid, error = validate_docker_compose(invalid_compose)
        
        assert is_valid is False
        assert error is not None
        assert "services" in error.lower() or "dictionary" in error.lower()
    
    async def test_compose_not_dict(self):
        """Test that compose root must be a dictionary"""
        invalid_compose = """- just
- a
- list
"""
        
        is_valid, error = validate_docker_compose(invalid_compose)
        
        assert is_valid is False
        assert error is not None
    
    async def test_empty_compose(self):
        """Test that empty compose is rejected"""
        is_valid, error = validate_docker_compose("")
        
        assert is_valid is False
        assert error is not None
    
    async def test_compose_with_only_comments(self):
        """Test that compose with only comments is rejected"""
        invalid_compose = """# Just comments
# No actual content
"""
        
        is_valid, error = validate_docker_compose(invalid_compose)
        
        assert is_valid is False
        assert error is not None
    
    async def test_complex_valid_compose(self):
        """Test complex but valid docker-compose.yml"""
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
        
        is_valid, error = validate_docker_compose(complex_compose)
        
        assert is_valid is True
        assert error is None

