# GitHub Actions Workflows

## Overview

DockLite использует GitHub Actions для автоматического тестирования:
- ✅ **CI** - Unit тесты (backend + frontend)
- ✅ **E2E** - End-to-end тесты с Playwright
- ✅ **Setup Dev** - Проверка `./docklite setup-dev`
- ✅ **Type Check** - Проверка типов

---

## 🌐 E2E Tests

**Файл:** `test-e2e.yml`

### Назначение

Запускает полные end-to-end тесты через Playwright для проверки реальных пользовательских сценариев.

### Когда запускается

- ✅ При пуше в `main` или `dev` (если изменены frontend/backend/docker-compose)
- ✅ При создании Pull Request
- ✅ Вручную через GitHub Actions UI

### Что проверяется

**24 E2E теста:**

#### Authentication (7 tests)
- Login form display
- Admin/user login
- Invalid credentials
- Logout
- Session persistence
- Protected routes

#### Admin User (9 tests)
- Access all views (Projects, Users, Containers, Traefik)
- See system containers
- System containers protection
- Create project/user dialogs
- Multi-tenant view

#### Non-Admin User (8 tests)
- Limited navigation
- See only own projects
- NOT see system containers
- NOT access admin pages

### Workflow Steps

```yaml
1. Checkout code
2. Setup Python 3.11 + Node.js 20
3. Install dependencies (npm ci + Playwright browsers)
4. Start DockLite (docker compose up)
5. Wait for services (health checks)
6. Create test users (cursor, testuser)
7. Run Playwright tests
8. Upload artifacts (reports, videos)
9. Cleanup (docker compose down)
```

### Test Users

Создаются автоматически:
- **cursor** (admin) - password: `CursorAI_Test2024!`
- **testuser** (user) - password: `TestUser_2024!`

### Artifacts

#### Playwright Report (always)
- Полный отчет о тестах
- Сохраняется 30 дней
- Просмотр: Скачать артефакт и открыть index.html

#### Test Videos (on failure)
- Видео-записи упавших тестов
- Сохраняется 7 дней
- Помогает в отладке

### Service Logs

При падении автоматически собираются логи:
- Backend logs
- Frontend logs
- Traefik logs

### Typical Run Time

- ⏱️ Setup: ~3-4 минуты
- ⏱️ Tests: ~1-2 минуты (24 tests)
- ⏱️ Total: ~5-6 минут

### Local Testing

Запустите локально перед пушем:
```bash
# Setup
cd frontend
npm install @playwright/test
npx playwright install chromium

# Create test users
./docklite add-user cursor -p "CursorAI_Test2024!" --admin
./docklite add-user testuser -p "TestUser_2024!" --user

# Run tests
./docklite test-e2e           # Headless
./docklite test-e2e --ui      # Interactive (recommended)
./docklite test-e2e --headed  # Show browser
```

### Troubleshooting

#### Tests timeout
- Increase timeout in `playwright.config.js`
- Check service health endpoints
- Review service logs

#### Flaky tests
- Add explicit waits: `waitForLoadState('networkidle')`
- Increase wait times for slow operations
- Run with `--workers=1` for serial execution

#### Authentication failures
- Verify test users created successfully
- Check JWT secret consistency
- Review auth flow logs

---

## 🧪 Test Development Setup

**Файл:** `test-setup-dev.yml`

### Назначение

Автоматически проверяет что команда `./docklite setup-dev` корректно работает на разных платформах и версиях Python.

### Когда запускается

- ✅ При пуше в `main` или `dev` ветки (если изменены скрипты или CLI)
- ✅ При создании Pull Request в `main` или `dev`
- ✅ Вручную через GitHub Actions UI (workflow_dispatch)

### Что проверяется

#### 1. Linux (Ubuntu Latest)

- Создание виртуального окружения `.venv/`
- Установка зависимостей в venv
- Создание `.env` файла
- Работа CLI команд (`version`, `--help`)
- Автоматическое использование venv CLI-wrapper'ом
- Идемпотентность (повторный запуск `setup-dev`)

#### 2. macOS (Latest)

- Все проверки как для Linux
- **Дополнительно:** Проверка что пакеты НЕ устанавливаются в user site-packages
- Проверка что не используется `--break-system-packages`
- Отсутствие загрязнения системного Python

#### 3. Множественные версии Python

Тестирование на Python:
- 3.8 (минимальная поддерживаемая версия)
- 3.9
- 3.10
- 3.11
- 3.12 (latest)

### Проверки

```bash
# 1. venv создан
test -d .venv

# 2. Python в venv существует
test -f .venv/bin/python

# 3. Зависимости установлены
.venv/bin/python -c "import typer, rich, dotenv, yaml"

# 4. .env файл создан
test -f .env

# 5. CLI работает
./docklite version

# 6. CLI использует venv
./docklite version  # должен работать без ручной активации venv

# 7. Идемпотентность
./docklite setup-dev  # повторный запуск не должен падать

# 8. Чистота системы (macOS)
python3 -m pip list --user  # не должно быть typer/rich
```

### Как запустить вручную

1. Перейдите в GitHub → Actions
2. Выберите "Test Development Setup"
3. Нажмите "Run workflow"
4. Выберите ветку
5. Нажмите "Run workflow"

### Ожидаемый результат

✅ **Все 3 джобы зелёные:**
- `test-setup-linux` ✅
- `test-setup-macos` ✅
- `test-setup-multiple-python` ✅
- `summary` ✅

### При ошибках

#### ModuleNotFoundError в venv

```bash
# Проверьте что зависимости установлены
cat scripts/requirements.txt

# Проверьте версии
.venv/bin/pip list
```

#### CLI не находит venv

```bash
# Проверьте docklite wrapper
cat docklite | head -20

# Должен быть код:
# if not in venv:
#     venv_python = venv_path / "bin" / "python"
#     if venv_python.exists():
#         os.execv(str(venv_python), ...)
```

#### macOS: пакеты в user site-packages

```bash
# Проверьте что не используется --user или --break-system-packages
grep -r "\-\-user" scripts/
grep -r "break-system-packages" scripts/

# Должно быть пусто!
```

### Добавление новых проверок

Добавьте шаг в `test-setup-dev.yml`:

```yaml
- name: Your new check
  run: |
    # Your test commands
    if [ condition ]; then
      echo "✅ Check passed"
    else
      echo "❌ Check failed"
      exit 1
    fi
```

### Связанные файлы

- `scripts/cli/commands/development.py` - команда `setup-dev`
- `scripts/development/setup-dev.sh` - bash-версия (deprecated)
- `docklite` - CLI wrapper с auto-venv
- `scripts/requirements.txt` - зависимости CLI
- `.env.example` - шаблон конфигурации

### Производительность

Типичное время выполнения:
- Linux: ~2-3 минуты
- macOS: ~3-4 минуты
- Multiple Python: ~8-10 минут (параллельно)

**Итого:** ~4-5 минут для полной проверки

### Почему это важно

1. ✅ **Кросс-платформенность** - гарантирует работу на Linux и macOS
2. ✅ **Совместимость Python** - тестирует Python 3.8-3.12
3. ✅ **Чистота системы** - проверяет что не загрязняется system Python
4. ✅ **Предотвращение регрессий** - ловит поломки до мержа
5. ✅ **Документация работой** - показывает как должно работать

### Примеры использования

#### Локальное тестирование перед пушем

```bash
# Эмулируйте CI локально
./docklite setup-dev
.venv/bin/python -c "import typer, rich, dotenv, yaml"
./docklite version
./docklite --help

# Проверьте идемпотентность
./docklite setup-dev  # должно пройти без ошибок

# Проверьте чистоту (macOS)
python3 -m pip list --user | grep -E "(typer|rich)"  # должно быть пусто
```

#### Тестирование на конкретной версии Python

```bash
# Создайте venv с нужной версией
python3.9 -m venv .venv-test
source .venv-test/bin/activate
pip install -r scripts/requirements.txt

# Проверьте CLI
./docklite version
```

---

**Автор:** DockLite Team  
**Обновлено:** 2024-10  
**Статус:** ✅ Production Ready

