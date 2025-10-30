# Core Module Tests

Tests for DockLite core functionality (security and configuration).

## Test Files

### test_security.py (16 tests)
Tests for authentication and authorization dependencies:
- `get_current_user` - JWT token validation
- `get_current_active_user` - Active user check
- `get_current_user_with_cookie` - Traefik ForwardAuth support
- Token priority: Bearer header > Cookie
- Security edge cases: expired tokens, malformed JWT, wrong secret

### test_config.py (21 tests)
Tests for configuration management:
- Default values validation
- Environment variable overrides
- Settings singleton
- Configuration validation
- .env file handling

## Running Tests

```bash
# All core tests
pytest tests/test_core/ -v

# Specific file
pytest tests/test_core/test_security.py -v
pytest tests/test_core/test_config.py -v

# With coverage
pytest tests/test_core/ --cov=app.core --cov-report=term-missing
```

## Coverage

- **test_security.py**: Covers `app/core/security.py` (~95% coverage)
- **test_config.py**: Covers `app/core/config.py` (~90% coverage)

