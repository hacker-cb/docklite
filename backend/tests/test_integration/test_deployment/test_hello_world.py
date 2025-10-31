"""
Integration tests for Hello World example deployments.

These tests deploy actual projects from example presets and verify they are
accessible via Traefik routing. They test the full deployment workflow:
1. Copy example files to project directory
2. Create project via API
3. Deploy containers via docker compose
4. Access via Traefik domain routing
5. Verify HTTP responses
6. Cleanup
"""

from __future__ import annotations

import pytest
import time
import subprocess
import json
import shutil
from pathlib import Path
from httpx import AsyncClient
import httpx

from app.presets.examples import (
    FLASK_HELLO,
    FASTAPI_HELLO,
    EXPRESS_HELLO,
    FULLSTACK_HELLO,
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_flask_hello_world_deployment(
    client: AsyncClient, auth_headers: dict
):
    """Test Flask single-service deployment via Traefik"""
    from app.core.config import settings
    
    domain = "flask-test.localhost"

    try:
        # 1. Create project via API first (writes docker-compose.yml with Traefik labels)
        response = await client.post(
            "/api/projects",
            json={
                "name": "Test Flask Hello",
                "domain": domain,
                "compose_content": FLASK_HELLO.compose_content,
                "env_vars": {},
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        project_data = response.json()
        project_id = project_data["id"]
        project_slug = project_data["slug"]  # Use slug from API response
        
        # Now we know the actual slug the API created
        project_dir = Path(settings.PROJECTS_DIR) / project_slug

        # 2. Copy app files (docker-compose.yml already created by API with labels)
        assert project_dir.exists(), f"Project directory not created: {project_dir}"
        assert project_dir.is_dir(), f"Project path is not a directory: {project_dir}"
        assert (project_dir / "docker-compose.yml").exists(), "docker-compose.yml not created by API"
        
        example_path = Path(__file__).parent.parent.parent.parent / "app" / "presets" / "examples" / "flask-hello"
        for item in example_path.iterdir():
            if item.name != "docker-compose.yml":  # Skip compose file - API already wrote it with labels
                if item.is_file():
                    shutil.copy2(item, project_dir / item.name)  # Copy TO project_dir/filename
                elif item.is_dir():
                    shutil.copytree(item, project_dir / item.name, dirs_exist_ok=True)

        # 3. Deploy containers
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"Docker compose up failed: {result.stderr}"
        
        # Give containers extra time to pull images and install dependencies
        print(f"Waiting 15s for {domain} to install dependencies...")
        time.sleep(15)

        # 4. Wait for container health (retry logic with generous timeouts)
        max_attempts = 30  # Increased for CI environment
        wait_time = 3  # Seconds between retries
        print(f"Waiting for {domain} to be ready...")
        
        for attempt in range(max_attempts):
            try:
                health_response = httpx.get(
                    "http://localhost/health", 
                    headers={"Host": domain}, 
                    timeout=10.0,
                    follow_redirects=True
                )
                if health_response.status_code == 200:
                    print(f"Health check passed on attempt {attempt + 1}")
                    # Give Traefik and app a moment to fully stabilize
                    time.sleep(2)
                    break
            except (httpx.RequestError, httpx.TimeoutException) as e:
                if attempt == max_attempts - 1:
                    print(f"Health check failed after {max_attempts} attempts")
                    # Try to get container logs for debugging
                    logs_result = subprocess.run(
                        ["docker", "compose", "logs"],
                        cwd=project_dir,
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    print(f"Container logs:\n{logs_result.stdout}")
                    raise AssertionError(f"Container not ready after {max_attempts * wait_time}s: {e}")
                print(f"Attempt {attempt + 1}/{max_attempts}: {type(e).__name__}")
                time.sleep(wait_time)

        # 5. Verify root endpoint
        response_data = httpx.get("http://localhost/", headers={"Host": domain}, timeout=10.0)
        if response_data.status_code != 200:
            print(f"ERROR: Root endpoint returned {response_data.status_code}")
            print(f"Response headers: {response_data.headers}")
            print(f"Response body: {response_data.text[:500]}")
            # Get container logs
            logs_result = subprocess.run(
                ["docker", "compose", "logs", "--tail=50"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=10,
            )
            print(f"Container logs:\n{logs_result.stdout}")
        assert response_data.status_code == 200, f"Root endpoint returned {response_data.status_code}: {response_data.text[:200]}"
        data = response_data.json()
        assert data["message"] == "Hello World from Flask!"
        assert data["framework"] == "Flask"

        # 6. Verify health endpoint
        health = httpx.get("http://localhost/health", headers={"Host": domain}, timeout=5.0)
        assert health.status_code == 200
        assert health.json()["status"] == "healthy"

        # 7. Verify Content-Type
        assert "application/json" in health.headers.get("content-type", "")

    finally:
        # Cleanup: stop containers and delete project
        if project_dir.exists():
            subprocess.run(
                ["docker", "compose", "down", "-v"],
                cwd=project_dir,
                capture_output=True,
                timeout=30,
            )
            shutil.rmtree(project_dir, ignore_errors=True)

        # Delete project from database
        try:
            await client.delete(f"/api/projects/{project_id}", headers=auth_headers)
        except:
            pass


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fastapi_hello_world_deployment(
    client: AsyncClient, auth_headers: dict
):
    """Test FastAPI single-service deployment via Traefik"""
    from app.core.config import settings
    
    domain = "fastapi-test.localhost"

    try:
        # 1. Create project via API first (writes docker-compose.yml with Traefik labels)
        response = await client.post(
            "/api/projects",
            json={
                "name": "Test FastAPI Hello",
                "domain": domain,
                "compose_content": FASTAPI_HELLO.compose_content,
                "env_vars": {},
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        project_data = response.json()
        project_id = project_data["id"]
        project_slug = project_data["slug"]
        project_dir = Path(settings.PROJECTS_DIR) / project_slug

        # 2. Copy app files (docker-compose.yml already created by API with labels)
        assert project_dir.exists() and project_dir.is_dir(), f"Project directory issue: {project_dir}"
        
        example_path = Path(__file__).parent.parent.parent.parent / "app" / "presets" / "examples" / "fastapi-hello"
        for item in example_path.iterdir():
            if item.name != "docker-compose.yml":
                if item.is_file():
                    shutil.copy2(item, project_dir / item.name)
                elif item.is_dir():
                    shutil.copytree(item, project_dir / item.name, dirs_exist_ok=True)

        # 3. Deploy
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        
        # Give containers extra time to pull images and install dependencies
        print(f"Waiting 15s for {domain} to install dependencies...")
        time.sleep(15)

        # 4. Wait for health (retry logic with generous timeouts)
        max_attempts = 30
        wait_time = 3
        print(f"Waiting for {domain} to be ready...")
        
        for attempt in range(max_attempts):
            try:
                health_response = httpx.get(
                    "http://localhost/health", 
                    headers={"Host": domain}, 
                    timeout=10.0,
                    follow_redirects=True
                )
                if health_response.status_code == 200:
                    print(f"Health check passed on attempt {attempt + 1}")
                    time.sleep(2)
                    break
            except (httpx.RequestError, httpx.TimeoutException) as e:
                if attempt == max_attempts - 1:
                    print(f"Health check failed after {max_attempts} attempts")
                    logs_result = subprocess.run(
                        ["docker", "compose", "logs"],
                        cwd=project_dir,
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    print(f"Container logs:\n{logs_result.stdout}")
                    raise AssertionError(f"Container not ready after {max_attempts * wait_time}s: {e}")
                print(f"Attempt {attempt + 1}/{max_attempts}: {type(e).__name__}")
                time.sleep(wait_time)

        # 5. Verify root endpoint
        response_data = httpx.get("http://localhost/", headers={"Host": domain}, timeout=10.0)
        assert response_data.status_code == 200
        data = response_data.json()
        assert data["message"] == "Hello World from FastAPI!"
        assert data["framework"] == "FastAPI"

        # 6. Verify health
        health = httpx.get("http://localhost/health", headers={"Host": domain}, timeout=5.0)
        assert health.status_code == 200
        assert health.json()["status"] == "healthy"

        # 7. Verify OpenAPI docs (unique to FastAPI)
        docs_response = httpx.get("http://localhost/docs", headers={"Host": domain}, timeout=5.0)
        assert docs_response.status_code == 200
        assert "swagger" in docs_response.text.lower()

        # 8. Verify OpenAPI JSON schema
        openapi_response = httpx.get("http://localhost/openapi.json", headers={"Host": domain}, timeout=5.0)
        assert openapi_response.status_code == 200
        schema = openapi_response.json()
        assert "openapi" in schema
        assert "/health" in schema.get("paths", {})

    finally:
        # Cleanup
        if project_dir.exists():
            subprocess.run(
                ["docker", "compose", "down", "-v"],
                cwd=project_dir,
                capture_output=True,
                timeout=30,
            )
            shutil.rmtree(project_dir, ignore_errors=True)

        try:
            await client.delete(f"/api/projects/{project_id}", headers=auth_headers)
        except:
            pass


@pytest.mark.integration
@pytest.mark.asyncio
async def test_express_hello_world_deployment(
    client: AsyncClient, auth_headers: dict
):
    """Test Express single-service deployment via Traefik"""
    from app.core.config import settings
    
    domain = "express-test.localhost"

    try:
        # 1. Create project via API first (writes docker-compose.yml with Traefik labels)
        response = await client.post(
            "/api/projects",
            json={
                "name": "Test Express Hello",
                "domain": domain,
                "compose_content": EXPRESS_HELLO.compose_content,
                "env_vars": {},
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        project_data = response.json()
        project_id = project_data["id"]
        project_slug = project_data["slug"]
        project_dir = Path(settings.PROJECTS_DIR) / project_slug

        # 2. Copy app files (docker-compose.yml already created by API with labels)
        assert project_dir.exists() and project_dir.is_dir(), f"Project directory issue: {project_dir}"
        
        example_path = Path(__file__).parent.parent.parent.parent / "app" / "presets" / "examples" / "express-hello"
        for item in example_path.iterdir():
            if item.name != "docker-compose.yml":
                if item.is_file():
                    shutil.copy2(item, project_dir / item.name)
                elif item.is_dir():
                    shutil.copytree(item, project_dir / item.name, dirs_exist_ok=True)

        # 3. Deploy
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        
        # Give containers extra time to pull images and install dependencies
        print(f"Waiting 15s for {domain} to install dependencies...")
        time.sleep(15)

        # 4. Wait for health (retry logic with generous timeouts)
        max_attempts = 30
        wait_time = 3
        print(f"Waiting for {domain} to be ready...")
        
        for attempt in range(max_attempts):
            try:
                health_response = httpx.get(
                    "http://localhost/health", 
                    headers={"Host": domain}, 
                    timeout=10.0,
                    follow_redirects=True
                )
                if health_response.status_code == 200:
                    print(f"Health check passed on attempt {attempt + 1}")
                    time.sleep(2)
                    break
            except (httpx.RequestError, httpx.TimeoutException) as e:
                if attempt == max_attempts - 1:
                    print(f"Health check failed after {max_attempts} attempts")
                    logs_result = subprocess.run(
                        ["docker", "compose", "logs"],
                        cwd=project_dir,
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    print(f"Container logs:\n{logs_result.stdout}")
                    raise AssertionError(f"Container not ready after {max_attempts * wait_time}s: {e}")
                print(f"Attempt {attempt + 1}/{max_attempts}: {type(e).__name__}")
                time.sleep(wait_time)

        # 5. Verify root endpoint
        response_data = httpx.get("http://localhost/", headers={"Host": domain}, timeout=10.0)
        assert response_data.status_code == 200
        data = response_data.json()
        assert data["message"] == "Hello World from Express!"
        assert data["framework"] == "Express"

        # 6. Verify health
        health = httpx.get("http://localhost/health", headers={"Host": domain}, timeout=5.0)
        assert health.status_code == 200
        assert health.json()["status"] == "healthy"

        # 7. Verify Express headers
        assert "x-powered-by" in [k.lower() for k in health.headers.keys()]

        # 8. Verify runtime info
        info_response = httpx.get("http://localhost/info", headers={"Host": domain}, timeout=5.0)
        assert info_response.status_code == 200
        info_data = info_response.json()
        assert "node" in info_data["runtime"].lower()

    finally:
        # Cleanup
        if project_dir.exists():
            subprocess.run(
                ["docker", "compose", "down", "-v"],
                cwd=project_dir,
                capture_output=True,
                timeout=30,
            )
            shutil.rmtree(project_dir, ignore_errors=True)

        try:
            await client.delete(f"/api/projects/{project_id}", headers=auth_headers)
        except:
            pass


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fullstack_hello_world_deployment(
    client: AsyncClient, auth_headers: dict
):
    """Test multi-service (frontend + backend) deployment via Traefik"""
    from app.core.config import settings
    
    domain = "fullstack-test.local"  # Changed from .localhost to .local

    try:
        # 1. Create project via API first (writes docker-compose.yml with Traefik labels)
        response = await client.post(
            "/api/projects",
            json={
                "name": "Test Full Stack Hello",
                "domain": domain,
                "compose_content": FULLSTACK_HELLO.compose_content,
                "env_vars": {},
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        project_data = response.json()
        project_id = project_data["id"]
        project_slug = project_data["slug"]
        project_dir = Path(settings.PROJECTS_DIR) / project_slug

        # 2. Copy app files (docker-compose.yml already created by API with labels)
        assert project_dir.exists() and project_dir.is_dir(), f"Project directory issue: {project_dir}"
        
        example_path = Path(__file__).parent.parent.parent.parent / "app" / "presets" / "examples" / "fullstack-hello"
        for item in example_path.iterdir():
            if item.name != "docker-compose.yml":
                if item.is_file():
                    shutil.copy2(item, project_dir / item.name)
                elif item.is_dir():
                    shutil.copytree(item, project_dir / item.name, dirs_exist_ok=True)

        # 3. Deploy
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        
        # Give containers extra time to pull images and install dependencies
        # Fullstack needs more time: 2 containers (frontend nginx + backend flask)
        print(f"Waiting 25s for {domain} to install dependencies (fullstack: 2 containers)...")
        time.sleep(25)
        
        # DEBUG: Check Traefik routers to see actual configuration
        print("\n=== TRAEFIK ROUTERS DEBUG ===")
        traefik_routers = subprocess.run(
            ["docker", "exec", "docklite-traefik", "wget", "-q", "-O-", "http://localhost:8080/api/http/routers"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if traefik_routers.returncode == 0:
            import json
            try:
                routers_data = json.loads(traefik_routers.stdout)
                print(f"Found {len(routers_data)} Traefik routers:")
                for router in routers_data:
                    name = router.get('name', '')
                    if 'fullstack' in name.lower() or 'docklite' in name.lower():
                        print(f"  - {name}:")
                        print(f"      rule: {router.get('rule')}")
                        print(f"      priority: {router.get('priority')}")
                        print(f"      service: {router.get('service')}")
                        print(f"      status: {router.get('status')}")
            except Exception as e:
                print(f"Failed to parse: {e}")
                print(f"Raw response (first 1000 chars):\n{traefik_routers.stdout[:1000]}")
        else:
            print(f"Failed to query Traefik API: {traefik_routers.stderr}")
        print("=== END DEBUG ===\n")

        # 4. Wait for backend health via API proxy (retry logic with generous timeouts)
        max_attempts = 30
        wait_time = 3
        print(f"Waiting for {domain} backend to be ready...")
        
        for attempt in range(max_attempts):
            try:
                health_response = httpx.get(
                    "http://localhost/api/health", 
                    headers={"Host": domain}, 
                    timeout=10.0,
                    follow_redirects=True
                )
                if health_response.status_code == 200:
                    print(f"Backend health check passed on attempt {attempt + 1}")
                    time.sleep(2)
                    break
            except (httpx.RequestError, httpx.TimeoutException) as e:
                if attempt == max_attempts - 1:
                    print(f"Backend health check failed after {max_attempts} attempts")
                    logs_result = subprocess.run(
                        ["docker", "compose", "logs"],
                        cwd=project_dir,
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    print(f"Container logs:\n{logs_result.stdout}")
                    raise AssertionError(f"Backend not ready after {max_attempts * wait_time}s: {e}")
                print(f"Attempt {attempt + 1}/{max_attempts}: {type(e).__name__}")
                time.sleep(wait_time)

        # 5. Verify frontend HTML is served
        frontend_response = httpx.get("http://localhost/", headers={"Host": domain}, timeout=10.0)
        assert frontend_response.status_code == 200
        assert "text/html" in frontend_response.headers.get("content-type", "")
        assert "Full Stack" in frontend_response.text

        # 6. Verify backend API via proxy path
        api_response = httpx.get("http://localhost/api/message", headers={"Host": domain}, timeout=5.0)
        if api_response.status_code != 200:
            print(f"ERROR: /api/message returned {api_response.status_code}")
            print(f"Response text: {api_response.text}")
            # Try direct backend access (without /api prefix to test nginx proxy)
            try:
                direct_test = httpx.get("http://localhost/message", headers={"Host": domain}, timeout=5.0)
                print(f"Direct /message test: {direct_test.status_code}")
            except Exception as e:
                print(f"Direct /message failed: {e}")
            # Get backend logs
            logs_result = subprocess.run(
                ["docker", "compose", "logs", "backend"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=10,
            )
            print(f"Backend logs:\n{logs_result.stdout}")
        assert api_response.status_code == 200, f"/api/message returned {api_response.status_code}: {api_response.text}"
        api_data = api_response.json()
        assert api_data["message"] == "Hello from Backend API!"
        assert api_data["stack"] == "Flask + Nginx"

        # 7. Verify backend health
        health = httpx.get("http://localhost/api/health", headers={"Host": domain}, timeout=5.0)
        assert health.status_code == 200
        assert health.json()["status"] == "healthy"

        # 8. Verify both containers are running
        ps_result = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
        containers = []
        for line in ps_result.stdout.strip().split("\n"):
            if line:
                containers.append(json.loads(line))

        assert len(containers) == 2  # frontend + backend
        assert all(c["State"] == "running" for c in containers)

    finally:
        # Cleanup
        if project_dir.exists():
            subprocess.run(
                ["docker", "compose", "down", "-v"],
                cwd=project_dir,
                capture_output=True,
                timeout=30,
            )
            shutil.rmtree(project_dir, ignore_errors=True)

        try:
            await client.delete(f"/api/projects/{project_id}", headers=auth_headers)
        except:
            pass

