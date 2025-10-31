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
    client: AsyncClient, auth_headers: dict, temp_projects_dir: str
):
    """Test Flask single-service deployment via Traefik"""
    project_slug = "test-flask-hello"
    domain = "flask-test.localhost"
    project_dir = Path(temp_projects_dir) / project_slug

    try:
        # 1. Copy example files to project directory
        example_path = Path(__file__).parent.parent.parent.parent / "app" / "presets" / "examples" / "flask-hello"
        project_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(example_path, project_dir, dirs_exist_ok=True)

        # 2. Create project via API
        response = await client.post(
            "/api/projects",
            json={
                "name": "Test Flask Hello",
                "slug": project_slug,
                "domain": domain,
                "compose_content": FLASK_HELLO.compose_content,
                "env_vars": {},
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        project_data = response.json()
        project_id = project_data["id"]

        # 3. Deploy containers
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"Docker compose up failed: {result.stderr}"

        # 4. Wait for container health (retry logic)
        max_attempts = 15
        for attempt in range(max_attempts):
            try:
                health_response = httpx.get("http://localhost/health", headers={"Host": domain}, timeout=5.0)
                if health_response.status_code == 200:
                    break
            except (httpx.RequestError, httpx.TimeoutException):
                if attempt == max_attempts - 1:
                    raise
                time.sleep(2)

        # 5. Verify root endpoint
        response_data = httpx.get("http://localhost/", headers={"Host": domain}, timeout=5.0)
        assert response_data.status_code == 200
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
    client: AsyncClient, auth_headers: dict, temp_projects_dir: str
):
    """Test FastAPI single-service deployment via Traefik"""
    project_slug = "test-fastapi-hello"
    domain = "fastapi-test.localhost"
    project_dir = Path(temp_projects_dir) / project_slug

    try:
        # 1. Copy example files
        example_path = Path(__file__).parent.parent.parent.parent / "app" / "presets" / "examples" / "fastapi-hello"
        project_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(example_path, project_dir, dirs_exist_ok=True)

        # 2. Create project
        response = await client.post(
            "/api/projects",
            json={
                "name": "Test FastAPI Hello",
                "slug": project_slug,
                "domain": domain,
                "compose_content": FASTAPI_HELLO.compose_content,
                "env_vars": {},
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        project_id = response.json()["id"]

        # 3. Deploy
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0

        # 4. Wait for health
        max_attempts = 15
        for attempt in range(max_attempts):
            try:
                health_response = httpx.get("http://localhost/health", headers={"Host": domain}, timeout=5.0)
                if health_response.status_code == 200:
                    break
            except (httpx.RequestError, httpx.TimeoutException):
                if attempt == max_attempts - 1:
                    raise
                time.sleep(2)

        # 5. Verify root endpoint
        response_data = httpx.get("http://localhost/", headers={"Host": domain}, timeout=5.0)
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
    client: AsyncClient, auth_headers: dict, temp_projects_dir: str
):
    """Test Express single-service deployment via Traefik"""
    project_slug = "test-express-hello"
    domain = "express-test.localhost"
    project_dir = Path(temp_projects_dir) / project_slug

    try:
        # 1. Copy example files
        example_path = Path(__file__).parent.parent.parent.parent / "app" / "presets" / "examples" / "express-hello"
        project_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(example_path, project_dir, dirs_exist_ok=True)

        # 2. Create project
        response = await client.post(
            "/api/projects",
            json={
                "name": "Test Express Hello",
                "slug": project_slug,
                "domain": domain,
                "compose_content": EXPRESS_HELLO.compose_content,
                "env_vars": {},
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        project_id = response.json()["id"]

        # 3. Deploy
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0

        # 4. Wait for health
        max_attempts = 15
        for attempt in range(max_attempts):
            try:
                health_response = httpx.get("http://localhost/health", headers={"Host": domain}, timeout=5.0)
                if health_response.status_code == 200:
                    break
            except (httpx.RequestError, httpx.TimeoutException):
                if attempt == max_attempts - 1:
                    raise
                time.sleep(2)

        # 5. Verify root endpoint
        response_data = httpx.get("http://localhost/", headers={"Host": domain}, timeout=5.0)
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
    client: AsyncClient, auth_headers: dict, temp_projects_dir: str
):
    """Test multi-service (frontend + backend) deployment via Traefik"""
    project_slug = "test-fullstack-hello"
    domain = "fullstack-test.localhost"
    project_dir = Path(temp_projects_dir) / project_slug

    try:
        # 1. Copy example files
        example_path = Path(__file__).parent.parent.parent.parent / "app" / "presets" / "examples" / "fullstack-hello"
        project_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(example_path, project_dir, dirs_exist_ok=True)

        # 2. Create project
        response = await client.post(
            "/api/projects",
            json={
                "name": "Test Full Stack Hello",
                "slug": project_slug,
                "domain": domain,
                "compose_content": FULLSTACK_HELLO.compose_content,
                "env_vars": {},
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        project_id = response.json()["id"]

        # 3. Deploy
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0

        # 4. Wait for backend health via API proxy
        max_attempts = 15
        for attempt in range(max_attempts):
            try:
                health_response = httpx.get("http://localhost/api/health", headers={"Host": domain}, timeout=5.0)
                if health_response.status_code == 200:
                    break
            except (httpx.RequestError, httpx.TimeoutException):
                if attempt == max_attempts - 1:
                    raise
                time.sleep(2)

        # 5. Verify frontend HTML is served
                frontend_response = httpx.get("http://localhost/", headers={"Host": domain}, timeout=5.0)
        assert frontend_response.status_code == 200
        assert "text/html" in frontend_response.headers.get("content-type", "")
        assert "Full Stack" in frontend_response.text

        # 6. Verify backend API via proxy path
        api_response = httpx.get("http://localhost/api/message", headers={"Host": domain}, timeout=5.0)
        assert api_response.status_code == 200
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

