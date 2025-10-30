# Service Module Tests

Tests for DockLite service layer (business logic and integrations).

## Test Files

### test_docker_service.py (22 tests) ✨ NEW
Tests for Docker CLI wrapper service:
- Docker service initialization
- List all/running containers
- Get specific container
- Start/stop/restart operations
- Remove containers (normal and force)
- Container logs retrieval
- Container stats parsing
- System container protection (docklite-* prefix)

### test_auth_service.py (27 tests)
Tests for authentication service:
- Password hashing with bcrypt
- JWT token creation and validation
- User creation and authentication
- Duplicate username handling

### test_validation.py
Tests for validation services

### test_traefik_service.py (18 tests)
Tests for Traefik label injection:
- Label generation
- Compose modification
- Network configuration
- Port detection

## Running Tests

```bash
# All service tests
pytest tests/test_services/ -v

# Docker service only
pytest tests/test_services/test_docker_service.py -v

# With coverage
pytest tests/test_services/ --cov=app.services --cov-report=term-missing
```

## Coverage

- **test_docker_service.py**: Covers `app/services/docker_service.py` (~95% coverage)
- **test_auth_service.py**: Covers `app/services/auth_service.py` (~95% coverage)
- **test_traefik_service.py**: Covers `app/services/traefik_service.py` (~90% coverage)

## Important Notes

### Docker Service Tests
All Docker operations are **mocked** using `unittest.mock`. No real Docker commands are executed during testing. This ensures:
- ✅ Tests run fast
- ✅ No Docker daemon required
- ✅ Safe for CI/CD
- ✅ Predictable results

### Security Tests
Token validation tests use real JWT encoding/decoding but with test database and isolated sessions.

