# DockLite - Web Server Management System

![CI](https://github.com/hacker-cb/docklite/workflows/CI/badge.svg)
![Setup Dev](https://github.com/hacker-cb/docklite/actions/workflows/test-setup-dev.yml/badge.svg)
![E2E Tests](https://github.com/hacker-cb/docklite/actions/workflows/test-e2e.yml/badge.svg)
![Integration Tests](https://github.com/hacker-cb/docklite/actions/workflows/test-integration.yml/badge.svg)
![Type Check](https://github.com/hacker-cb/docklite/actions/workflows/type-check.yml/badge.svg)
[![codecov](https://codecov.io/gh/hacker-cb/docklite/branch/main/graph/badge.svg)](https://codecov.io/gh/hacker-cb/docklite)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

DockLite - это система управления веб-сервером с возможностью деплоя множества проектов через docker-compose. Система предоставляет удобный веб-интерфейс, REST API и professional CLI.

## 🚀 Quick Start

```bash
# Клонируйте репозиторий
git clone https://github.com/hacker-cb/docklite.git
cd docklite

# Настройте окружение разработки (автоматически)
./docklite dev setup-dev

# ИЛИ вручную:
# cp .env.example .env
# nano .env  # Укажите ваш HOSTNAME
# pip3 install --user -r scripts/requirements.txt

# Запустите систему
./docklite start

# Создайте первого админа
./docklite user add admin -p "YourPassword" --admin
```

Откройте в браузере: `http://your-server-hostname`

## ⚙️ Первоначальная настройка

Команда `./docklite dev setup-dev` автоматически:
- ✅ Проверяет Python 3.8+
- ✅ **Создает виртуальное окружение (.venv/)** 
- ✅ Устанавливает зависимости CLI в venv (typer, rich, python-dotenv, PyYAML)
- ✅ Создает .env файл из .env.example
- ✅ Проверяет Docker
- ✅ Делает CLI исполняемым

**Виртуальное окружение:** CLI автоматически использует `.venv/` - зависимости изолированы от системного Python. Вручную активировать venv **не нужно** - скрипт `./docklite` сам переключается на venv python.

## Возможности

### Управление Проектами
- **Multi-tenancy** - каждый проект принадлежит пользователю, изоляция по системным пользователям
- **Slug-based paths** - читаемые пути проектов (example-com-a7b2) вместо числовых ID
- **CRUD проектов** - создание, редактирование, удаление с проверкой прав владения
- **Готовые пресеты** - 14 шаблонов для популярных стеков (Nginx, WordPress, PostgreSQL, и др.)
- **SSH Deployment** - загрузка файлов через rsync/scp/SFTP для каждого системного пользователя
- **Управление .env переменными** - удобный интерфейс для настройки окружения
- **Валидация docker-compose.yml** - проверка корректности конфигурации перед деплоем

### Контейнеры и Инфраструктура
- **Docker управление** - запуск, остановка, перезапуск контейнеров
- **System protection** - защита системных контейнеров (backend, frontend, traefik) от случайной остановки
- **Traefik v3** - современный reverse proxy с domain-based routing
- **Мониторинг** - просмотр логов и статистики контейнеров

### Безопасность и Доступ
- **Авторизация (JWT)** - защищенный доступ с username/password
- **Role-based access control** - админы и обычные пользователи
- **User Management** - управление пользователями с привязкой к системным пользователям Linux
- **Traefik Dashboard** - доступ только для администраторов

### Интерфейс
- **Веб-интерфейс** - современный UI на Vue.js 3 + PrimeVue
- **REST API** - полное API для всех операций
- **CLI** - профессиональный CLI с 21 командой (6 root + 4 группы) и bash completion

## Архитектура

DockLite использует **multi-tenant** архитектуру, где каждый проект принадлежит пользователю и изолирован по системному пользователю Linux:

```
~/docklite/                     # Система DockLite
├── backend/                    # FastAPI backend
├── frontend/                   # Vue.js 3 + PrimeVue frontend
└── docker-compose.yml          # Traefik v3 + backend + frontend

/home/{system_user}/projects/   # Проекты пользователя
├── example-com-a7b2/          # Slug-based путь
│   ├── docker-compose.yml
│   └── .env
└── mysite-org-b3c8/
    ├── docker-compose.yml
    └── .env
```

**Multi-tenancy:**
- Каждый DockLite пользователь имеет `system_user` (Linux user)
- Проекты хранятся в `/home/{system_user}/projects/{slug}/`
- SSH деплой выполняется от имени `system_user`
- Пользователи видят только свои проекты (админы видят все)

## Технологический стек

- **Backend**: FastAPI, SQLAlchemy, Alembic, PyYAML
- **Frontend**: Vue.js 3 + PrimeVue + Vite
- **Database**: SQLite (с возможностью миграции на PostgreSQL)
- **Reverse Proxy**: Traefik v3
- **Deployment**: Docker, docker-compose
- **Testing**: Pytest (243 unit + 3 integration tests), Vitest (120+ tests), Playwright (24 E2E tests)

## Установка

### Требования

- Docker
- Docker Compose
- Git

### Установка Docker (если не установлен)

```bash
# Обновить пакеты
sudo apt update

# Установить зависимости
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Добавить GPG ключ Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавить репозиторий Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установить Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Добавить пользователя в группу docker
sudo usermod -aG docker $USER

# Перелогиниться или выполнить
newgrp docker

# Проверить установку
docker --version
docker compose version
```

### Шаги установки DockLite

1. **Клонировать репозиторий** (или убедиться, что файлы уже на сервере):

```bash
cd ~
# Если репозиторий существует, то git clone не нужен
```

2. **Настроить переменные окружения**:

```bash
cd ~/docklite
cp .env.example .env
# Отредактируйте .env файл и установите SECRET_KEY
```

3. **Создать системного пользователя для деплоя**:

```bash
cd ~/docklite
sudo ./docklite deploy setup-user
```

4. **Настроить SSH (для localhost)**:

```bash
sudo ./docklite deploy setup-ssh
```

5. **Запустить систему**:

```bash
./docklite start
```

6. **Проверить статус**:

```bash
./docklite status
```

## Использование

### Веб-интерфейс

После запуска системы, веб-интерфейс будет доступен:

**Используя системный hostname:**
- **Frontend**: http://example.com (или ваш hostname)
- **Backend API**: http://example.com/api
- **API Docs**: http://example.com/docs
- **Traefik Dashboard**: http://example.com/traefik/ (admin-only)

**Локальный доступ:**
- **Frontend**: http://localhost
- **Backend API**: http://localhost/api
- **API Docs**: http://localhost/docs
- **Traefik**: http://localhost/traefik/ (admin-only)

**Примечание:** DockLite использует умную логику определения hostname:
1. **Приоритет 1**: Значение `HOSTNAME` в `.env` файле (если задано)
2. **Приоритет 2**: Системный hostname из команды `hostname`
3. **Fallback**: "localhost"

**Traefik v3** автоматически маршрутизирует запросы к правильным сервисам без необходимости указывать порты. Все работает через стандартный HTTP порт 80. Подробнее: [TRAEFIK.md](./TRAEFIK.md)

### Первый вход (Initial Setup)

При первом открытии UI вы увидите экран **"Initial Setup"**:

1. Откройте frontend (http://localhost)
2. Увидите форму "Create Admin Account"
3. Заполните:
   - **Username**: ваш логин (мин. 3 символа)
   - **Email**: ваш email (опционально)
   - **Password**: пароль (мин. 6 символов)
   - **Confirm Password**: повторите пароль
4. Нажмите "Create Admin Account"
5. Автоматический вход в систему

**Это нужно сделать только один раз!** При последующих визитах будет обычная форма входа.

### Дополнительные пользователи

Для создания дополнительных пользователей используйте CLI:

```bash
# Создать обычного пользователя
./docklite add-user john -p "SecurePass123"

# Создать администратора  
./docklite add-user admin -p "AdminPass123" --admin

# С email
./docklite add-user user@example.com -p "Pass123" -e user@example.com

# Список всех пользователей
./docklite list-users
```

Также можно создавать через веб-интерфейс:

1. Войдите как админ
2. Откройте раздел "Users"
3. Нажмите "New User"
4. Заполните данные и нажмите "Create"

### Создание проекта

#### Из пресета (рекомендуется)

1. Откройте веб-интерфейс
2. Нажмите "New Project"
3. Выберите вкладку "From Preset"
4. Выберите категорию (Web, Backend, Database, CMS)
5. Кликните на нужный пресет (например, Nginx, WordPress, PostgreSQL)
6. Заполните:
   - **Name**: Имя проекта
   - **Domain**: Домен проекта (например, example.com)
7. Нажмите "Create"

**Traefik автоматически настроит роутинг** - проект будет доступен по указанному домену через порт 80.

#### Custom docker-compose

1. Нажмите "New Project"
2. Выберите вкладку "Custom"
3. Вставьте свой docker-compose.yml
4. Заполните Name и Domain
5. Нажмите "Create"

**Доступные пресеты**: 14 шаблонов (см. [PRESETS.md](./PRESETS.md))

**Примечание**: Traefik labels автоматически добавляются к вашему `docker-compose.yml`, обеспечивая domain-based routing без необходимости управления портами.

### Деплой проекта на сервер

После создания проекта в UI, загрузите файлы приложения через SSH:

```bash
# 1. Загрузить файлы (например, Project ID = 5)
rsync -avz ./your-app/ docklite@server:/home/docklite/projects/5/

# 2. Запустить docker-compose
ssh docklite@server "cd /home/docklite/projects/5 && docker-compose up -d"

# 3. Проверить статус
ssh docklite@server "cd /home/docklite/projects/5 && docker-compose ps"
```

**Первоначальная настройка сервера**:

```bash
cd ~/docklite
sudo ./setup-docklite-user.sh
```

Подробная документация: [SSH_ACCESS.md](./SSH_ACCESS.md)

### Редактирование .env переменных

1. В списке проектов нажмите на иконку шестеренки
2. Добавьте или измените переменные окружения
3. Нажмите "Save"

### API Endpoints

#### Проекты

- `GET /api/projects` - получить список всех проектов
- `POST /api/projects` - создать новый проект
- `GET /api/projects/{id}` - получить проект по ID
- `PUT /api/projects/{id}` - обновить проект
- `DELETE /api/projects/{id}` - удалить проект

#### Environment Variables

- `GET /api/projects/{id}/env` - получить переменные окружения
- `PUT /api/projects/{id}/env` - обновить переменные окружения

### Пример docker-compose.yml для проекта

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html
```

## Разработка

### Первоначальная настройка

```bash
# Один раз при первом клонировании
./docklite setup-dev

# Создает:
# - .venv/ - виртуальное окружение для CLI
# - .env - конфигурация из .env.example
# - Устанавливает зависимости в venv
```

### Backend (в Docker)

```bash
# Backend работает в Docker контейнере
docker compose up -d backend

# Логи
docker compose logs -f backend

# Тесты
docker compose exec backend pytest -v
```

**Разработка вне Docker (опционально):**
```bash
cd backend

# Создать виртуальное окружение (требует python3-venv)
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
uvicorn app.main:app --reload
```

### Frontend

```bash
cd ~/docklite/frontend

# Установить зависимости
npm install

# Запустить dev сервер
npm run dev

# Сборка для продакшена
npm run build
```

### Миграции БД

```bash
cd ~/docklite/backend

# Создать новую миграцию
alembic revision --autogenerate -m "description"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1
```

## Управление

### Ежедневные команды (Root Level)

Основные команды для работы с системой:

```bash
./docklite start            # Запустить систему
./docklite stop             # Остановить систему
./docklite restart          # Перезапустить систему
./docklite logs             # Показать логи всех контейнеров
./docklite logs backend     # Логи конкретного контейнера
./docklite status           # Статус системы
./docklite status -v        # Детальный статус
./docklite test             # Запустить все тесты
```

### Группы команд

DockLite использует логическую группировку команд по функциям:

**Development (`dev`)** - Разработка и тестирование:
```bash
./docklite dev setup-dev       # Первоначальная настройка окружения
./docklite dev rebuild         # Пересобрать Docker образы
./docklite dev test-backend    # Тесты бэкенда
./docklite dev test-frontend   # Тесты фронтенда
./docklite dev test-e2e        # E2E тесты (Playwright)
./docklite dev test-cli        # Тесты CLI (pytest)
```

**Deployment (`deploy`)** - Деплой на production (Linux only):
```bash
./docklite deploy setup-user   # Создать системного пользователя
./docklite deploy setup-ssh    # Настроить SSH доступ
./docklite deploy init-db      # Инициализировать/сбросить БД
```

**User Management (`user`)** - Управление пользователями:
```bash
./docklite user add admin -p "Pass" --admin    # Добавить админа
./docklite user add username                   # Добавить пользователя (пароль в интерактивном режиме)
./docklite user list                           # Список пользователей
./docklite user list --verbose                 # Детальная информация
./docklite user reset-password username        # Сбросить пароль
```

**Maintenance (`maint`)** - Обслуживание системы:
```bash
./docklite maint backup                        # Создать резервную копию
./docklite maint restore backups/file.tar.gz   # Восстановить из бэкапа
./docklite maint clean --all                   # Очистить неиспользуемые ресурсы
```

### Примеры использования

```bash
# Первый запуск
./docklite dev setup-dev                       # Настроить окружение
./docklite start                               # Запустить систему
./docklite user add admin -p "pass" --admin    # Создать админа

# Разработка
./docklite dev rebuild --no-cache              # Полная пересборка
./docklite logs -f                             # Следить за логами
./docklite test                                # Прогнать тесты

# Обслуживание
./docklite maint backup                        # Бэкап перед обновлением
./docklite status -v                           # Проверить систему
./docklite maint clean --images                # Очистить образы
```

**Полная документация:** [scripts/README.md](mdc:scripts/README.md)

## Тестирование

DockLite имеет комплексное покрытие тестами на всех уровнях:
- **Backend**: 244 тестов (pytest) - API, Services, Validators, Utils, Integration
- **Frontend Unit**: 120+ тестов (vitest) - Components, Views, Composables, Utils, Router
- **E2E**: 24 теста (playwright) - User flows, authentication, multi-tenancy
- **Integration**: 4 теста (pytest) - Real project deployment via Traefik
- **Total**: 392+ тестов
- **Coverage**: ~95%

### Запуск тестов

```bash
# Все тесты сразу (backend + frontend unit)
./docklite test

# Только backend (244 tests, includes 4 integration tests)
./docklite test-backend

# Только frontend unit (120+ tests)
./docklite test-frontend

# E2E tests (24 tests) - требует установки Playwright
cd frontend && npm run test:e2e

# С опциями
./docklite test-backend -v       # Verbose output
./docklite test-backend -k auth  # Auth tests only
./docklite test-backend --cov    # With coverage report
./docklite test-frontend --watch # Watch mode
./docklite test-frontend --ui    # Interactive UI
```

### E2E тесты (Playwright)

E2E тесты проверяют реальные пользовательские сценарии через браузер:

**Покрытие:**
- ✅ Авторизация (admin и user)
- ✅ Разграничение прав доступа
- ✅ Управление проектами
- ✅ Управление контейнерами
- ✅ Multi-tenancy изоляция
- ✅ Защита системных контейнеров

**Установка и запуск:**
```bash
# Установка (однократно)
cd frontend
npm install --save-dev @playwright/test
npx playwright install chromium

# Создать тестовых пользователей
./docklite add-user cursor -p "CursorAI_Test2024!" --admin
./docklite add-user testuser -p "TestUser_2024!" --user

# Запуск
npm run test:e2e              # Все E2E тесты
npm run test:e2e:ui           # Интерактивный режим
npm run test:e2e:debug        # Режим отладки
```

**Подробнее:** 
- [HOW_TO_RUN_TESTS.md](./HOW_TO_RUN_TESTS.md) - Подробное руководство
- [E2E_TESTS.md](./E2E_TESTS.md) - E2E тестирование с Playwright
- [frontend/tests/e2e/README.md](./frontend/tests/e2e/README.md) - E2E тесты (техническая документация)
- [scripts/README.md](./scripts/README.md) - CLI команды

## Текущий статус

### ✅ Реализованные возможности

**Основная функциональность:**
- Multi-tenant архитектура с изоляцией пользователей
- CRUD API для проектов с валидацией
- Управление .env переменными
- 14 готовых пресетов для популярных стеков
- Валидация docker-compose.yml и проверка конфликтов портов

**Безопасность и доступ:**
- JWT авторизация с role-based access control
- Управление пользователями (админ/user)
- Защита системных контейнеров от случайной остановки

**Контейнеры и инфраструктура:**
- Docker управление (start, stop, restart, logs, stats)
- Traefik v3 reverse proxy с domain-based routing
- Traefik Dashboard с защитой (admin-only)
- Мониторинг всех контейнеров

**Интерфейс и инструменты:**
- Современный Vue.js 3 + PrimeVue UI
- Professional CLI (21 команда + bash completion)
- Comprehensive testing (380+ tests including E2E, 95% coverage)

### 🔄 В планах

- SSL/HTTPS с Let's Encrypt
- Расширенное логирование и мониторинг
- Backup и восстановление
- MCP Server для AI агентов

## 📚 Документация

### Руководства

- [QUICKSTART.md](./QUICKSTART.md) - Быстрый старт для новых пользователей
- [SETUP.md](./SETUP.md) - Подробная настройка окружения разработки
- [DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md) - Руководство по деплою
- [SSH_ACCESS.md](./SSH_ACCESS.md) - Настройка SSH доступа
- [HOW_TO_RUN_TESTS.md](./HOW_TO_RUN_TESTS.md) - Руководство по тестированию
- [E2E_TESTS.md](./E2E_TESTS.md) - E2E тестирование с Playwright

### Техническая документация

- [TRAEFIK.md](./TRAEFIK.md) - Traefik v3 reverse proxy и routing
- [PRESETS.md](./PRESETS.md) - 14 шаблонов docker-compose
- [SYSTEM_CONTAINERS_PROTECTION.md](./SYSTEM_CONTAINERS_PROTECTION.md) - Защита системных контейнеров
- [scripts/README.md](./scripts/README.md) - CLI команды и скрипты
- [scripts/completion/README.md](./scripts/completion/README.md) - Bash completion

### CI/CD

- [docs/CI_CD.md](./docs/CI_CD.md) - GitHub Actions workflows и автоматическое тестирование
- [.github/workflows/README.md](./.github/workflows/README.md) - Подробности о workflow
- [docs/diagrams/ci-workflow.md](./docs/diagrams/ci-workflow.md) - Диаграммы CI pipeline

## Поддержка

Для сообщений об ошибках и предложений по улучшению, создайте issue в репозитории проекта.

## Лицензия

MIT License


### Bash Completion

Установите умное автодополнение для CLI:

```bash
./docklite install-completion
source ~/.bashrc
```

Теперь можно использовать Tab для автодополнения команд, опций, имен сервисов и файлов!

**Документация:** [scripts/completion/README.md](mdc:scripts/completion/README.md)

