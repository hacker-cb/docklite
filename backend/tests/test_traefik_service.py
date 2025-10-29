"""
Tests for TraefikService
"""
import pytest
from app.services.traefik_service import TraefikService


class TestTraefikLabelsGeneration:
    """Test Traefik labels generation"""
    
    def test_generate_labels_basic(self):
        """Test basic label generation"""
        labels = TraefikService.generate_labels(
            domain="example.com",
            slug="example-com-1",
            internal_port=80
        )
        
        assert len(labels) == 4
        assert "traefik.enable=true" in labels
        assert "traefik.http.routers.example-com-1.rule=Host(`example.com`)" in labels
        assert "traefik.http.routers.example-com-1.entrypoints=web" in labels
        assert "traefik.http.services.example-com-1.loadbalancer.server.port=80" in labels
    
    def test_generate_labels_custom_port(self):
        """Test label generation with custom port"""
        labels = TraefikService.generate_labels(
            domain="api.example.com",
            slug="api-example-com-2",
            internal_port=8000
        )
        
        assert "traefik.http.services.api-example-com-2.loadbalancer.server.port=8000" in labels
    
    def test_generate_labels_slug_sanitization(self):
        """Test that special characters in slug are sanitized"""
        labels = TraefikService.generate_labels(
            domain="example.com",
            slug="example_com__1",  # Underscores should be converted to hyphens
            internal_port=80
        )
        
        # Slug in router name should be sanitized
        assert any("example-com--1" in label for label in labels)


class TestPortDetection:
    """Test internal port detection from compose"""
    
    def test_detect_port_from_expose(self):
        """Test port detection from expose section"""
        compose = """
version: '3.8'
services:
  web:
    image: nginx:alpine
    expose:
      - "8080"
"""
        port = TraefikService.detect_internal_port(compose)
        assert port == 8080
    
    def test_detect_port_from_ports(self):
        """Test port detection from ports mapping"""
        compose = """
version: '3.8'
services:
  web:
    image: nginx:alpine
    ports:
      - "3000:80"
"""
        port = TraefikService.detect_internal_port(compose)
        assert port == 80  # Should extract internal port (after :)
    
    def test_detect_port_from_ports_with_env(self):
        """Test port detection from ports with env variables"""
        compose = """
version: '3.8'
services:
  web:
    image: nginx:alpine
    ports:
      - "${PORT:-8080}:80"
"""
        port = TraefikService.detect_internal_port(compose)
        assert port == 80
    
    def test_detect_port_default(self):
        """Test default port when none specified"""
        compose = """
version: '3.8'
services:
  web:
    image: nginx:alpine
"""
        port = TraefikService.detect_internal_port(compose)
        assert port == 80  # Default
    
    def test_detect_port_invalid_compose(self):
        """Test port detection with invalid compose"""
        compose = "invalid yaml content {["
        port = TraefikService.detect_internal_port(compose)
        assert port == 80  # Default fallback


class TestLabelsInjection:
    """Test Traefik labels injection into compose"""
    
    def test_inject_labels_simple(self):
        """Test injecting labels into simple compose file"""
        compose = """version: '3.8'
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
"""
        modified, error = TraefikService.inject_labels_to_compose(
            compose,
            domain="example.com",
            slug="example-com-1"
        )
        
        assert error is None
        assert "traefik.enable=true" in modified
        assert "Host(`example.com`)" in modified
        assert "docklite-network" in modified
        # Ports should be removed
        assert "8080:80" not in modified
        # Expose should be added
        assert "80" in modified
    
    def test_inject_labels_replaces_existing(self):
        """Test that existing Traefik labels are replaced"""
        compose = """version: '3.8'
services:
  web:
    image: nginx:alpine
    labels:
      - "traefik.enable=false"
      - "traefik.http.routers.old.rule=Host(`old.com`)"
      - "custom.label=keep-me"
"""
        modified, error = TraefikService.inject_labels_to_compose(
            compose,
            domain="example.com",
            slug="example-com-1"
        )
        
        assert error is None
        assert "traefik.enable=true" in modified  # Updated
        assert "Host(`example.com`)" in modified  # New domain
        assert "old.com" not in modified  # Old removed
        assert "custom.label=keep-me" in modified  # Custom label preserved
    
    def test_inject_labels_adds_network(self):
        """Test that docklite-network is added"""
        compose = """version: '3.8'
services:
  web:
    image: nginx:alpine
"""
        modified, error = TraefikService.inject_labels_to_compose(
            compose,
            domain="example.com",
            slug="example-com-1"
        )
        
        assert error is None
        assert "docklite-network" in modified
        assert "external: true" in modified
    
    def test_inject_labels_preserves_existing_network(self):
        """Test that existing networks are preserved"""
        compose = """version: '3.8'
services:
  web:
    image: nginx:alpine
    networks:
      - backend
networks:
  backend:
"""
        modified, error = TraefikService.inject_labels_to_compose(
            compose,
            domain="example.com",
            slug="example-com-1"
        )
        
        assert error is None
        assert "backend" in modified
        assert "docklite-network" in modified
    
    def test_inject_labels_multi_service(self):
        """Test injecting labels into compose with multiple services"""
        compose = """version: '3.8'
services:
  app:
    image: myapp:latest
    ports:
      - "3000:3000"
  db:
    image: postgres:15
"""
        modified, error = TraefikService.inject_labels_to_compose(
            compose,
            domain="example.com",
            slug="example-com-1"
        )
        
        assert error is None
        # Labels should be added to first service only
        lines = modified.split('\n')
        app_section_start = next(i for i, line in enumerate(lines) if 'app:' in line)
        db_section_start = next(i for i, line in enumerate(lines) if 'db:' in line)
        
        # Check that traefik labels are in app section
        app_section = '\n'.join(lines[app_section_start:db_section_start])
        assert "traefik.enable=true" in app_section
    
    def test_inject_labels_force_port(self):
        """Test forcing specific internal port"""
        compose = """version: '3.8'
services:
  web:
    image: nginx:alpine
"""
        modified, error = TraefikService.inject_labels_to_compose(
            compose,
            domain="example.com",
            slug="example-com-1",
            force_internal_port=8080
        )
        
        assert error is None
        assert "loadbalancer.server.port=8080" in modified
    
    def test_inject_labels_invalid_compose(self):
        """Test injecting labels into invalid compose"""
        compose = "invalid yaml content {["
        
        modified, error = TraefikService.inject_labels_to_compose(
            compose,
            domain="example.com",
            slug="example-com-1"
        )
        
        assert error is not None
        # Error message can be YAML parsing error, no services found, or generic error
        assert any(phrase in error for phrase in ["YAML parsing error", "Error injecting labels", "No services found"])
    
    def test_inject_labels_empty_compose(self):
        """Test injecting labels into empty compose"""
        compose = ""
        
        modified, error = TraefikService.inject_labels_to_compose(
            compose,
            domain="example.com",
            slug="example-com-1"
        )
        
        assert error is not None
        assert "Empty compose file" in error
    
    def test_inject_labels_no_services(self):
        """Test injecting labels when no services section"""
        compose = """version: '3.8'
volumes:
  data:
"""
        modified, error = TraefikService.inject_labels_to_compose(
            compose,
            domain="example.com",
            slug="example-com-1"
        )
        
        assert error is not None
        assert "No services found" in error


class TestUpdateLabels:
    """Test update_labels_in_compose (alias method)"""
    
    def test_update_labels_alias(self):
        """Test that update_labels_in_compose works as alias"""
        compose = """version: '3.8'
services:
  web:
    image: nginx:alpine
"""
        modified, error = TraefikService.update_labels_in_compose(
            compose,
            domain="example.com",
            slug="example-com-1"
        )
        
        assert error is None
        assert "traefik.enable=true" in modified

