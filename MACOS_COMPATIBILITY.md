# DockLite - macOS Compatibility Report

**Status:** ✅ Полностью совместимо с macOS для разработки

## ✅ Что работает на macOS

### Docker
- ✅ Docker Desktop установлен и работает
- ✅ Docker socket доступен: `/var/run/docker.sock`
- ✅ `docker` и `docker compose` команды работают
- ✅ Контейнеры запускаются и управляются

### Основной цикл разработки
- ✅ Сборка образов (`docker compose build`)
- ✅ Запуск сервисов (`docker compose up`)
- ✅ Тестирование (backend pytest + frontend vitest)
- ✅ Логи и отладка
- ✅ Работа с контейнерами

### Файловая система
- ✅ Все пути адаптированы и работают автоматически
- ✅ Volume mappings работают корректно
- ✅ Hot-reload для разработки (backend + frontend)

### Python CLI
- ✅ Python 3.14 установлен
- ✅ Все зависимости доступны через pip
- ✅ CLI команды работают после адаптации

### Hostname Detection
- ✅ Автоопределение hostname работает
- ✅ Fallback на `localhost` для локальной разработки
- ✅ `.env` файл поддерживается

## ⚠️ Что НЕ работает (и не нужно)

### Linux-specific команды (только для production)
- ❌ `useradd`, `usermod` - управление системными пользователями
- ❌ `sg docker` - переключение группы docker
- ❌ `hostnamectl` - systemd утилита для hostname
- ❌ Deployment скрипты (`setup-user`, `setup-ssh`)

**Важно:** Эти команды нужны **только для production deployment на Linux сервере**. Для локальной разработки на macOS они не требуются.

## 🔧 Изменения для macOS

### 1. Автоопределение путей

**До:**
```python
PROJECT_ROOT = Path("/home/pavel/docklite")  # Hardcoded
```

**После:**
```python
# Auto-detect based on script location
SCRIPTS_DIR = Path(__file__).parent.parent.absolute()
PROJECT_ROOT = SCRIPTS_DIR.parent
```

**Результат:** Работает на любой ОС, в любой директории

### 2. Docker group detection

**До:**
```bash
# Always use sg docker
sg docker -c "docker-compose up"
```

**После:**
```bash
# Check if sg exists (Linux only)
if command -v sg &> /dev/null && ! groups | grep -q docker; then
    sg docker -c "docker-compose up"
else
    docker-compose up  # macOS or in docker group
fi
```

**Результат:** На macOS запускается напрямую, на Linux использует `sg` при необходимости

### 3. Python docker utils

```python
def has_docker_group() -> bool:
    """Check if current user is in docker group (Linux-specific)."""
    try:
        # On macOS, docker group doesn't exist
        if not shutil.which("sg"):
            return True  # Skip group switching
        
        docker_group = grp.getgrnam('docker')
        return docker_group.gr_gid in os.getgroups()
    except (KeyError, OSError):
        return True  # No group switching needed
```

**Результат:** Автоматически определяет macOS и пропускает sg

## 📋 Рабочий процесс на macOS

### Setup (один раз)

```bash
# 1. Установить Python зависимости
pip3 install typer rich python-dotenv pytest

# 2. Создать .env файл
cat > .env << 'EOF'
HOSTNAME=localhost
TRAEFIK_DASHBOARD_HOST=localhost
PROJECTS_DIR=/Users/pavel/docklite-projects
SECRET_KEY=dev-secret-key-change-in-production
EOF

# 3. Сделать CLI исполняемым
chmod +x scripts/docklite
```

### Разработка

```bash
# Запуск системы
./scripts/docklite start

# Или через docker compose напрямую
docker compose up -d

# Тесты
./scripts/docklite test              # Все тесты
./scripts/docklite test-backend      # Backend (240 тестов)
./scripts/docklite test-frontend     # Frontend (120+ тестов)

# Или напрямую
cd backend && pytest
cd frontend && npm test

# Логи
./scripts/docklite logs [service]
docker compose logs -f [service]

# Остановка
./scripts/docklite stop
docker compose down
```

### Доступ к сервисам

- **Frontend:** http://localhost
- **Backend API:** http://localhost/api
- **API Docs:** http://localhost/docs
- **Traefik Dashboard:** http://localhost/traefik (admin only)

## 🐳 Docker Compose

Работает **полностью** без изменений:

```bash
docker compose up -d          # Запуск
docker compose down           # Остановка
docker compose logs -f        # Логи
docker compose build          # Пересборка
docker compose ps             # Статус
```

## 🧪 Тестирование

### Backend (pytest)

```bash
# В контейнере (рекомендуется)
./scripts/docklite test-backend

# Локально
cd backend
pip install -r requirements.txt
pytest -v

# Конкретные тесты
pytest tests/test_api/
pytest tests/test_services/
pytest -k "test_traefik"
```

### Frontend (vitest)

```bash
# В контейнере
./scripts/docklite test-frontend

# Локально
cd frontend
npm install
npm test

# Watch mode
npm run test:watch
```

### CLI тесты

```bash
cd scripts
pytest tests/ -v
```

## 📦 Необходимые зависимости

### Обязательно
- ✅ Docker Desktop for Mac
- ✅ Python 3.8+ (у вас 3.14)
- ✅ Node.js 16+ (у вас 24.2)
- ✅ Git

### Python packages
```bash
pip3 install typer rich python-dotenv pytest
```

### Node packages (автоматически)
```bash
cd frontend && npm install
```

## 🚀 Production Deployment

Deployment на Linux сервер **с macOS**:

```bash
# 1. Подключиться к Linux серверу
ssh user@your-server.com

# 2. На сервере запустить deployment команды
./scripts/docklite setup-user
./scripts/docklite setup-ssh
./scripts/docklite init-db

# 3. С macOS деплоить через rsync/git
rsync -avz ./ user@server:/path/to/docklite/
```

**Важно:** Deployment команды (`setup-user`, `setup-ssh`) работают **только на Linux сервере**, не на macOS.

## 🎯 Выводы

### ✅ Для разработки на macOS

DockLite **полностью совместим** с macOS для разработки:
- Весь цикл разработки работает
- Тесты запускаются
- Docker контейнеры работают
- CLI адаптирован
- Hot-reload работает

### ⚠️ Ограничения

**Linux-specific функции** (для production):
- Deployment скрипты (требуют Linux)
- SSH setup (требует Linux)
- System user management (требует Linux)

**Решение:** Deployment выполняется на Linux сервере, не локально.

## 📝 Рекомендации

### Для разработки на macOS

1. **Используй Docker Compose напрямую:**
   ```bash
   docker compose up -d
   docker compose logs -f backend
   ```

2. **Или используй CLI для удобства:**
   ```bash
   ./scripts/docklite start
   ./scripts/docklite test
   ./scripts/docklite status
   ```

3. **Тесты запускай в контейнерах:**
   ```bash
   docker compose exec backend pytest
   docker compose exec frontend npm test
   ```

4. **Для production тестирования:**
   - Используй Linux VM (VirtualBox, UTM)
   - Или облачный Linux сервер
   - Или Docker Linux контейнер

### Git workflow

```bash
# На macOS разрабатываешь
git add .
git commit -m "Feature"
git push

# На Linux сервере деплоишь
ssh server
cd docklite
git pull
./scripts/docklite rebuild
```

## 🔍 Проверка работоспособности

```bash
# 1. Docker работает
docker ps

# 2. Python зависимости
python3 -c "import typer, rich; print('OK')"

# 3. Пути определяются корректно
cd scripts && python3 -c "from cli.config import PROJECT_ROOT; print(PROJECT_ROOT)"

# 4. Docker Compose
docker compose version

# 5. Запуск системы
docker compose up -d
docker compose ps

# 6. Доступ к UI
open http://localhost
```

## ❓ Частые вопросы

**Q: Могу ли я запустить все CLI команды на macOS?**  
A: Команды разработки (start, stop, test, logs) - да. Команды deployment (setup-user, setup-ssh) - нет, только на Linux.

**Q: Нужно ли мне настраивать docker группу на macOS?**  
A: Нет, Docker Desktop управляет правами автоматически.

**Q: Работает ли hot-reload на macOS?**  
A: Да, для backend (FastAPI) и frontend (Vue + Vite).

**Q: Можно ли деплоить на Linux с macOS?**  
A: Да, через SSH + git/rsync. Deployment команды запускаются на Linux сервере.

**Q: Нужен ли .env файл?**  
A: Да, но минимальный. Для разработки достаточно `HOSTNAME=localhost`.

## 📚 Дополнительная информация

- **README.md** - общая документация
- **QUICKSTART.md** - быстрый старт
- **TRAEFIK.md** - настройка Traefik
- **SSH_ACCESS.md** - deployment через SSH (Linux only)
- **TESTS.md** - запуск тестов

---

**Статус:** ✅ Готов к разработке на macOS  
**Дата:** 2025-10-30  
**Версия:** 1.0.0

