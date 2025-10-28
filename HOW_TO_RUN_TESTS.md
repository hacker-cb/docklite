# 🧪 Как запустить тесты DockLite

## ⚠️ Важно

Тесты написаны, но **НЕ запускались** так как Docker еще не установлен на сервере.

После установки Docker обязательно запустите тесты чтобы убедиться что все работает!

## 🚀 Быстрый запуск (когда Docker установлен)

### Способ 1: Через скрипт (рекомендуется)

```bash
cd /home/pavel/docklite
./run-tests.sh
```

Это запустит:
- Backend тесты (pytest) в контейнере
- Frontend тесты (vitest) локально (требует npm install)

### Способ 2: Вручную

**Backend тесты:**
```bash
cd /home/pavel/docklite
docker-compose run --rm backend pytest -v
```

**Frontend тесты:**
```bash
cd /home/pavel/docklite/frontend
npm install
npm test
```

## 📦 Backend тесты через Docker

### Запустить все backend тесты
```bash
docker-compose run --rm backend pytest -v
```

### Только тесты авторизации
```bash
docker-compose run --rm backend pytest tests/test_api/test_auth.py -v
```

### Только тесты projects
```bash
docker-compose run --rm backend pytest tests/test_api/test_projects.py -v
```

### С покрытием (coverage)
```bash
docker-compose run --rm backend pytest --cov=app --cov-report=term-missing
```

### С HTML отчетом
```bash
docker-compose run --rm backend pytest --cov=app --cov-report=html
# Отчет в: backend/htmlcov/index.html
```

## 🎨 Frontend тесты

### Предварительно: установить зависимости
```bash
cd /home/pavel/docklite/frontend
npm install
```

### Запустить все frontend тесты
```bash
npm test
```

### В watch режиме (авто-перезапуск)
```bash
npm test -- --watch
```

### С UI интерфейсом
```bash
npm run test:ui
```

### С покрытием
```bash
npm run test:coverage
# Отчет в: frontend/coverage/index.html
```

### Только auth тесты
```bash
npm test -- auth.spec.js
```

### Только forms тесты
```bash
npm test -- forms.spec.js
```

## 🔍 Первая проверка (before running full tests)

### Проверка синтаксиса Python

```bash
cd /home/pavel/docklite/backend

# Проверить все Python файлы
find app -name "*.py" -exec python3 -m py_compile {} \;
find tests -name "*.py" -exec python3 -m py_compile {} \;
```

### Проверка синтаксиса JavaScript

```bash
cd /home/pavel/docklite/frontend

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
cd /home/pavel/docklite
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

## 📊 Ожидаемые результаты

### Backend (60 тестов)
```
tests/test_api/test_projects.py::TestProjectsCRUD::test_create_project_success PASSED
tests/test_api/test_projects.py::TestProjectsCRUD::test_create_project_without_port PASSED
...
tests/test_api/test_auth.py::TestAuthSetup::test_setup_check_empty_db PASSED
tests/test_api/test_auth.py::TestAuthSetup::test_setup_create_first_admin PASSED
...
tests/test_services/test_auth_service.py::TestPasswordHashing::test_password_hash_creates_hash PASSED
...

============================== 60 passed in 3.2s ==============================
```

### Frontend (28 тестов)
```
✓ forms.spec.js (18 tests) 18ms
  ✓ Forms Structure Tests
    ✓ Project Creation Form (5)
    ✓ Projects Table (6)
    ✓ Environment Variables Form (3)
    ✓ Form Data Structure (1)
  ✓ Form Validation (3)

✓ auth.spec.js (10 tests) 22ms
  ✓ Setup Component (8)
  ✓ Login Component (4)
  ✓ App Authentication (2)

Test Files  2 passed (2)
     Tests  28 passed (28)
  Start at  10:30:15
  Duration  412ms
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

## 🎯 Быстрые команды

```bash
# Все тесты (одной командой)
cd /home/pavel/docklite && ./run-tests.sh

# Только backend
docker-compose run --rm backend pytest

# Только frontend
cd frontend && npm test

# Только auth тесты
docker-compose run --rm backend pytest tests/test_api/test_auth.py tests/test_services/test_auth_service.py

# С coverage
docker-compose run --rm backend pytest --cov=app

# Первый failed test останавливает выполнение
docker-compose run --rm backend pytest -x
```

## ✅ Чеклист первого запуска тестов

После установки Docker:

- [ ] Docker установлен и запущен
- [ ] `docker-compose build` выполнен
- [ ] Backend тесты: `docker-compose run --rm backend pytest -v`
- [ ] Frontend deps: `cd frontend && npm install`
- [ ] Frontend тесты: `cd frontend && npm test`
- [ ] Все тесты прошли успешно
- [ ] Coverage > 85%

## 📝 Примечания

**Тесты созданы но НЕ запускались** так как:
1. Docker не установлен на сервере
2. Нет виртуального окружения Python
3. Нет node_modules для frontend

После установки Docker и запуска `./start.sh` тесты должны заработать.

Если какие-то тесты fail - это нормально, нужно будет поправить импорты или мелкие баги.

---

**После установки Docker обязательно запустите**: `./run-tests.sh` 🧪

