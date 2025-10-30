# 🧪 How to Run DockLite Tests

## Test Coverage Overview

DockLite has comprehensive test coverage across multiple layers:
- ✅ **240 Backend tests** (pytest) - 95% coverage
- ✅ **120+ Frontend tests** (vitest) - unit tests
- ✅ **24 E2E tests** (playwright) - UI flows

**Total: 380+ tests**

## 🚀 Quick Start

### All Tests (Recommended)

```bash
./docklite test               # Run all tests (backend + frontend unit)
```

### Individual Test Suites

```bash
./docklite dev test-backend       # Backend only (240 tests)
./docklite dev test-frontend      # Frontend unit tests only (120+ tests)
./docklite dev test-e2e           # E2E tests (24 tests)
```

## 📦 Backend Tests (240 tests)

### Run All Backend Tests
```bash
./docklite dev test-backend
# or
docker compose exec backend pytest -v
```

### Specific Test Categories
```bash
# Authentication tests (34)
docker compose exec backend pytest -k security -v

# Traefik tests (18)
docker compose exec backend pytest -k traefik -v

# Hostname tests (20)
docker compose exec backend pytest -k hostname -v

# Projects API tests
docker compose exec backend pytest tests/test_api/test_projects.py -v

# Containers API tests
docker compose exec backend pytest tests/test_api/test_containers.py -v
```

### With Coverage
```bash
docker compose exec backend pytest --cov=app --cov-report=term-missing
```

### HTML Coverage Report
```bash
docker compose exec backend pytest --cov=app --cov-report=html
# Report: backend/htmlcov/index.html
```

### Run Specific Test
```bash
docker compose exec backend pytest tests/test_api/test_auth.py::test_login_success -v
```

## 🎨 Frontend Unit Tests (120+ tests)

### Prerequisites
```bash
cd frontend
npm install
```

### Run All Unit Tests
```bash
./docklite dev test-frontend
# or
cd frontend && npm test
```

### Watch Mode (auto-reload)
```bash
cd frontend
npm test -- --watch
```

### UI Mode (interactive)
```bash
cd frontend
npm run test:ui
```

### With Coverage
```bash
cd frontend
npm run test:coverage
# Report: frontend/coverage/index.html
```

### Specific Test Files
```bash
cd frontend
npm test -- components/CreateProjectDialog.test.js
npm test -- composables/useProjects.test.js
npm test -- views/ContainersView.test.js
```

## 🌐 E2E Tests (24 tests)

E2E tests validate complete user flows through a real browser using Playwright.

### Prerequisites

1. **Install Playwright:**
```bash
cd frontend
npm install --save-dev @playwright/test
npx playwright install chromium
```

2. **Start DockLite:**
```bash
./docklite start
```

3. **Create test users:**
```bash
# Admin user (already exists)
./docklite add-user cursor -p "CursorAI_Test2024!" --admin

# Regular user (create if not exists)
./docklite add-user testuser -p "TestUser_2024!" --user
```

### Run All E2E Tests
```bash
cd frontend
npm run test:e2e
```

### Interactive Mode (UI)
```bash
cd frontend
npm run test:e2e:ui
```

### Debug Mode
```bash
cd frontend
npm run test:e2e:debug
```

### Specific Test Files
```bash
cd frontend
npx playwright test auth.spec.js      # Authentication tests (7)
npx playwright test admin.spec.js     # Admin user tests (9)
npx playwright test user.spec.js      # Non-admin user tests (8)
```

### View Test Report
```bash
cd frontend
npm run test:e2e:report
```

### E2E Test Coverage

**Authentication (7 tests):**
- ✅ Login form display
- ✅ Admin login
- ✅ User login
- ✅ Invalid credentials
- ✅ Logout
- ✅ Session persistence
- ✅ Protected routes

**Admin User (9 tests):**
- ✅ Access all views (Projects, Users, Containers, Traefik)
- ✅ See system containers
- ✅ System containers protection
- ✅ Create project dialog
- ✅ Add user dialog
- ✅ View all projects (multi-tenant)

**Non-Admin User (8 tests):**
- ✅ Limited navigation menu
- ✅ See only own projects
- ✅ NOT see system containers
- ✅ NOT access Users page
- ✅ NOT access Traefik page
- ✅ Create project dialog
- ✅ See own containers only

See detailed guide: [frontend/tests/e2e/README.md](frontend/tests/e2e/README.md)

## 🔍 Первая проверка (before running full tests)

### Проверка синтаксиса Python

```bash
cd ~/docklite/backend

# Проверить все Python файлы
find app -name "*.py" -exec python3 -m py_compile {} \;
find tests -name "*.py" -exec python3 -m py_compile {} \;
```

### Проверка синтаксиса JavaScript

```bash
cd ~/docklite/frontend

# Если есть Node.js
npx eslint src/ --ext .js,.vue
```

## 🐛 Troubleshooting

### Backend тесты не запускаются

**Проблема**: "Docker not found"
```bash
# Установить Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker
```

**Проблема**: "Image not found"
```bash
# Собрать образ
cd ~/docklite
docker-compose build backend
```

**Проблема**: "Permission denied"
```bash
# Добавить пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker
```

**Проблема**: "Module not found"
```bash
# Пересобрать с зависимостями
docker-compose build --no-cache backend
```

### Frontend тесты не запускаются

**Проблема**: "npm not found"
```bash
# Установить Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

**Проблема**: "Module not found"
```bash
# Установить зависимости
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Проблема**: "happy-dom error"
```bash
# Переустановить
npm install --save-dev happy-dom@latest
```

## 📊 Expected Results

### Backend (240 tests)
```
tests/test_api/test_projects.py ...................... PASSED
tests/test_api/test_auth.py .......................... PASSED
tests/test_api/test_containers.py .................... PASSED
tests/test_api/test_users.py ......................... PASSED
tests/test_services/test_traefik_service.py .......... PASSED
tests/test_utils/test_hostname.py .................... PASSED
...

============================== 240 passed in 5.8s ==============================
```

### Frontend Unit Tests (120+ tests)
```
✓ components/CreateProjectDialog.test.js (15)
✓ components/EnvVarsDialog.test.js (12)
✓ composables/useProjects.test.js (25)
✓ composables/useContainers.test.js (20)
✓ views/ContainersView.test.js (18)
✓ utils/formatters.test.js (30+)

Test Files  15 passed (15)
     Tests  120 passed (120)
  Duration  892ms
```

### E2E Tests (24 tests)
```
Running 24 tests using 1 worker

  ✓ auth.spec.js:5:1 › Authentication › should show login form (1.2s)
  ✓ auth.spec.js:15:1 › Authentication › should login with admin (2.1s)
  ✓ admin.spec.js:10:1 › Admin › should access Projects view (1.5s)
  ✓ admin.spec.js:20:1 › Admin › should access Users management (1.8s)
  ✓ user.spec.js:10:1 › Non-Admin › limited navigation menu (1.3s)
  ✓ user.spec.js:30:1 › Non-Admin › see only own projects (2.0s)
  ...

  24 passed (45s)
```

## 🔄 CI/CD (автоматический запуск)

### GitHub Actions (пример)

Создайте `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build backend
        run: docker-compose build backend
      - name: Run backend tests
        run: docker-compose run --rm backend pytest -v
  
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        working-directory: ./frontend
        run: npm install
      - name: Run frontend tests
        working-directory: ./frontend
        run: npm test
```

### GitLab CI (пример)

Создайте `.gitlab-ci.yml`:

```yaml
stages:
  - test

backend-tests:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker-compose build backend
    - docker-compose run --rm backend pytest -v

frontend-tests:
  stage: test
  image: node:20
  script:
    - cd frontend
    - npm install
    - npm test
```

## ⏰ Когда запускать тесты

### Перед каждым коммитом
```bash
./run-tests.sh
git commit -m "Your changes"
```

### После pull/merge
```bash
git pull
./rebuild.sh
./run-tests.sh
```

### Перед деплоем в production
```bash
./run-tests.sh
# Если passed:
./rebuild.sh
```

## 🎯 Quick Commands Cheat Sheet

```bash
# All tests (backend + frontend unit)
./docklite test

# Backend only (240 tests)
./docklite dev test-backend

# Frontend unit only (120+ tests)
./docklite dev test-frontend

# E2E only (24 tests)
./docklite dev test-e2e

# Specific backend test category
docker compose exec backend pytest -k traefik -v
docker compose exec backend pytest -k hostname -v
docker compose exec backend pytest -k security -v

# With coverage
docker compose exec backend pytest --cov=app

# Stop on first failure
docker compose exec backend pytest -x

# Verbose output
docker compose exec backend pytest -vv

# Show print statements
docker compose exec backend pytest -s

# E2E in UI mode (interactive)
cd frontend && npm run test:e2e:ui

# E2E debug mode
cd frontend && npm run test:e2e:debug
```

## ✅ First Time Setup Checklist

- [ ] DockLite is running: `./docklite start`
- [ ] Backend tests pass: `./docklite dev test-backend`
- [ ] Frontend deps installed: `cd frontend && npm install`
- [ ] Frontend tests pass: `./docklite dev test-frontend`
- [ ] Playwright installed: `cd frontend && npm install @playwright/test`
- [ ] Playwright browsers: `cd frontend && npx playwright install chromium`
- [ ] Test users created (cursor, testuser)
- [ ] E2E tests pass: `cd frontend && npm run test:e2e`
- [ ] All 380+ tests passing ✅

## 📝 Notes

### Test Organization

**Backend tests** (`backend/tests/`) - 240 tests:
- API endpoints (auth, projects, users, containers, presets, deployment)
- Services (auth, docker, traefik, project)
- Utils (hostname, formatters)
- Validators (compose, domain)
- Models and core functionality

**Frontend unit tests** (`frontend/tests/`) - 120+ tests:
- Components (dialogs, forms)
- Composables (useProjects, useContainers, usePresets)
- Views (ProjectsView, UsersView, ContainersView)
- Utils (formatters, toast)
- Router

**E2E tests** (`frontend/tests/e2e/`) - 24 tests:
- Authentication flows
- Admin user functionality
- Non-admin user restrictions
- Multi-tenancy isolation
- System containers protection

### CI/CD

See [docs/CI_CD.md](docs/CI_CD.md) for automated testing setup.

---

**Coverage:** 95% backend, 85% frontend unit tests ✅

