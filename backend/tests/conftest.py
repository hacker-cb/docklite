import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
import tempfile
import shutil
from pathlib import Path


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Test engine and session
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    """Create a fresh database session for each test"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session):
    """Create test client with test database"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def temp_projects_dir():
    """Create temporary directory for test projects"""
    temp_dir = tempfile.mkdtemp()
    original_dir = settings.PROJECTS_DIR
    settings.PROJECTS_DIR = temp_dir
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)
    settings.PROJECTS_DIR = original_dir


@pytest.fixture
def sample_compose_content():
    """Sample valid docker-compose.yml content"""
    return """version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
"""


@pytest.fixture
def sample_project_data(sample_compose_content):
    """Sample project data for creating projects"""
    return {
        "name": "test-project",
        "domain": "test.local",
        "compose_content": sample_compose_content,
        "env_vars": {
            "ENV": "test",
            "DEBUG": "true"
        }
    }


@pytest.fixture
def invalid_compose_content():
    """Invalid docker-compose.yml content"""
    return """this is not valid yaml: [[["""


@pytest.fixture
def compose_without_services():
    """docker-compose.yml without services"""
    return """version: '3.8'
name: myapp
"""


@pytest.fixture
async def auth_token(client, db_session):
    """Create a user and return auth token for tests"""
    from app.models.user import User
    from app.services.auth_service import AuthService
    
    # Create user directly in DB
    auth_service = AuthService(db_session)
    password_hash = auth_service.get_password_hash("testpass123")
    
    user = User(
        username="testadmin",
        email="test@example.com",
        password_hash=password_hash,
        is_active=1,
        is_admin=1
    )
    
    db_session.add(user)
    await db_session.commit()
    
    # Create token
    token = auth_service.create_access_token(data={"sub": user.username})
    return token


@pytest.fixture
def auth_headers(auth_token):
    """Get authorization headers with token"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
async def test_project(client, sample_project_data, auth_headers):
    """Create a test project and return its data"""
    response = await client.post(
        "/api/projects",
        json=sample_project_data,
        headers=auth_headers
    )
    assert response.status_code == 201
    return response.json()



