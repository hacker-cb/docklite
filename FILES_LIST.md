# 📁 DockLite - Полный список файлов

**Всего**: 64 файла

## Backend (35 файлов)

### Application (24 файла)
```
app/
├── __init__.py
├── main.py                      # Entry point, FastAPI app
├── api/
│   ├── __init__.py
│   ├── projects.py             # Projects CRUD API
│   ├── presets.py              # Presets API
│   └── deployment.py           # Deployment instructions API
├── core/
│   ├── __init__.py
│   ├── config.py               # Settings, .env configuration
│   └── database.py             # SQLAlchemy setup
├── models/
│   ├── __init__.py
│   ├── project.py              # Project model
│   └── schemas.py              # Pydantic schemas
├── services/
│   ├── __init__.py
│   └── project_service.py      # Business logic
└── presets/
    ├── __init__.py             # Preset base class
    ├── web.py                  # 3 web presets
    ├── backend.py              # 4 backend presets
    ├── databases.py            # 4 database presets
    ├── cms.py                  # 3 CMS presets
    └── registry.py             # Presets registry
```

### Tests (7 файлов)
```
tests/
├── __init__.py
├── conftest.py                  # Fixtures
├── test_api/
│   ├── __init__.py
│   ├── test_projects.py        # 12 tests
│   ├── test_env.py             # 6 tests
│   └── test_presets.py         # 6 tests
└── test_services/
    ├── __init__.py
    └── test_validation.py      # 9 tests
```

Total: 63 файлов в проекте
