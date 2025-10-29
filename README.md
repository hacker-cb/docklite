# DockLite - Web Server Management System

DockLite - это система управления веб-сервером с возможностью деплоя множества проектов через docker-compose. Система предоставляет удобный веб-интерфейс, REST API и MCP сервер для взаимодействия с AI агентами.

## Возможности

- ✅ **Multi-tenancy** - каждый проект принадлежит пользователю, изоляция по системным пользователям
- ✅ **Авторизация (JWT)** - защищенный доступ с username/password, role-based access control
- ✅ **User Management** - управление пользователями с привязкой к системным пользователям Linux
- ✅ **Slug-based paths** - читаемые пути проектов (example-com-a7b2) вместо числовых ID
- ✅ **Готовые пресеты** - 14 шаблонов для популярных стеков (Nginx, WordPress, PostgreSQL, и др.)
- ✅ **CRUD проектов** - создание, редактирование, удаление проектов с проверкой прав владения
- ✅ **SSH Deployment** - загрузка файлов через rsync/scp/SFTP для каждого системного пользователя
- ✅ **Управление .env переменными** - удобный интерфейс для настройки окружения
- ✅ **Валидация docker-compose.yml** - проверка корректности конфигурации перед деплоем
- ✅ **Управление контейнерами** - запуск, остановка, перезапуск с правами владельца
- ✅ **Веб-интерфейс** - современный UI на Vue.js 3 + PrimeVue
- 🔄 **Virtual Hosts** - автоматическое создание nginx конфигов (следующий этап)
- 🔄 **SSL/HTTPS** - автоматические сертификаты Let's Encrypt (в планах)
- 🔄 **MCP Server** - для интеграции с AI агентами (в планах)

## Архитектура

DockLite использует **multi-tenant** архитектуру, где каждый проект принадлежит пользователю и изолирован по системному пользователю Linux:

```
/home/pavel/docklite/           # Система DockLite
├── backend/                    # FastAPI backend
├── frontend/                   # Vue.js 3 + PrimeVue frontend
├── nginx/                      # Nginx конфигурация
└── docker-compose.yml

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

- **Backend**: FastAPI, SQLAlchemy, Alembic, docker-py, PyYAML
- **Frontend**: Vue.js 3 + PrimeVue + Vite
- **Database**: SQLite (с возможностью миграции на PostgreSQL)
- **Web Server**: Nginx
- **Deployment**: Docker, docker-compose

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
cd /home/pavel
# Если репозиторий существует, то git clone не нужен
```

2. **Создать директорию для проектов**:

```bash
mkdir -p /home/pavel/docklite-projects
```

3. **Настроить переменные окружения**:

```bash
cd /home/pavel/docklite
cp .env.example .env
# Отредактируйте .env файл и установите SECRET_KEY
```

4. **Запустить систему**:

```bash
cd /home/pavel/docklite
docker-compose up -d --build
```

5. **Проверить статус**:

```bash
docker-compose ps
```

## Использование

### Веб-интерфейс

После запуска системы, веб-интерфейс будет доступен по адресу:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Первый вход (Initial Setup)

При первом открытии UI вы увидите экран **"Initial Setup"**:

1. Откройте frontend (http://localhost:5173)
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
docker exec -it docklite-backend python create_user.py username password email@example.com

# Создать админа
docker exec -it docklite-backend python create_user.py username password email@example.com --admin
```

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
   - **Port**: Порт (предзаполнен автоматически)
7. Нажмите "Create"

#### Custom docker-compose

1. Нажмите "New Project"
2. Выберите вкладку "Custom"
3. Вставьте свой docker-compose.yml
4. Заполните Name, Domain, Port
5. Нажмите "Create"

**Доступные пресеты**: 14 шаблонов (см. [PRESETS.md](./PRESETS.md))

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
cd /home/pavel/docklite
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

### Backend

```bash
cd /home/pavel/docklite/backend

# Создать виртуальное окружение (требует python3-venv)
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
python app/main.py
```

### Frontend

```bash
cd /home/pavel/docklite/frontend

# Установить зависимости
npm install

# Запустить dev сервер
npm run dev

# Сборка для продакшена
npm run build
```

### Миграции БД

```bash
cd /home/pavel/docklite/backend

# Создать новую миграцию
alembic revision --autogenerate -m "description"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1
```

## Управление

### Логи

```bash
# Все логи
docker-compose logs -f

# Логи backend
docker-compose logs -f backend

# Логи frontend
docker-compose logs -f frontend
```

### Остановка

```bash
docker-compose down
```

### Перезапуск

```bash
docker-compose restart
```

### Обновление

```bash
# Быстрый способ
./rebuild.sh

# Или вручную
docker-compose down
git pull  # если используется git
docker-compose up -d --build
```

## Тестирование

DockLite имеет комплексное покрытие тестами:
- **Backend**: 78 тестов (pytest) - API, авторизация, user management, валидация
- **Frontend**: 28 тестов (vitest) - формы, auth, структура данных
- **Total**: 106 тестов
- **Coverage**: ~94%

### Запуск тестов

```bash
# Все тесты сразу
./run-tests.sh

# Только backend
cd backend && pytest -v

# Только frontend
cd frontend && npm test

# С покрытием
cd backend && pytest --cov=app --cov-report=html
cd frontend && npm run test:coverage
```

Подробная документация: [TESTS.md](./TESTS.md)

## Текущий статус (Фаза 1)

### ✅ Реализовано

- [x] Структура проекта
- [x] SQLite + SQLAlchemy + Alembic
- [x] Модель Project с уникальными доменами
- [x] CRUD API для проектов
- [x] Валидация docker-compose.yml
- [x] Проверка конфликтов портов
- [x] Управление .env переменными
- [x] Vue.js 3 + PrimeVue интерфейс
- [x] Dockerfile и docker-compose.yml

### 🔄 В планах (следующие фазы)

- [ ] Авторизация (JWT) - Фаза 2
- [ ] Управление контейнерами (start/stop/restart) - Фаза 3
- [ ] Nginx и Virtual Hosts - Фаза 5
- [ ] SSL/HTTPS (Let's Encrypt) - Фаза 6
- [ ] Просмотр логов - Фаза 7
- [ ] MCP Server для AI агентов - Фаза 8

## Поддержка

Для сообщений об ошибках и предложений по улучшению, создайте issue в репозитории проекта.

## Лицензия

MIT License

