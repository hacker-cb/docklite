# DockLite Presets Guide

## Что такое пресеты?

Пресеты - это готовые шаблоны docker-compose конфигураций для быстрого создания типовых проектов.

**🔄 Traefik Integration:** Все пресеты автоматически настраиваются для работы с Traefik reverse proxy. Маршрутизация происходит по доменному имени, не нужно указывать порты вручную. Traefik labels добавляются автоматически при создании проекта.

## Доступные пресеты

### Web Servers (3)

1. **Nginx Static Site** 🌐
   - Статический сайт на Nginx
   - Внутренний порт: 80 (автоматически проксируется через Traefik)
   
2. **Apache Static Site** 🪶
   - Статический сайт на Apache
   - Внутренний порт: 80 (автоматически проксируется через Traefik)

3. **Nginx Reverse Proxy** 🔀
   - Nginx как обратный прокси для внутренних сервисов
   - Внутренний порт: 80 (автоматически проксируется через Traefik)
   - Примечание: Это application-level прокси, не путать с Traefik (system-level)

### Backend Frameworks (4)

4. **Node.js + Express** 💚
   - Node.js приложение с Express
   - Внутренний порт: 3000

5. **Python + FastAPI** 🐍
   - Python API с FastAPI
   - Внутренний порт: 8000

6. **Python + Flask** 🌶️
   - Python веб-приложение на Flask
   - Внутренний порт: 5000

7. **PHP + Laravel** 🐘
   - PHP приложение на Laravel
   - Внутренний порт: 80

### Databases (4)

8. **PostgreSQL + pgAdmin** 🐘
   - PostgreSQL с веб-админкой
   - pgAdmin внутренний порт: 80
   - Includes: postgres-data volume

9. **MySQL + phpMyAdmin** 🐬
   - MySQL с phpMyAdmin
   - phpMyAdmin внутренний порт: 80
   - Includes: mysql-data volume

10. **MongoDB + Mongo Express** 🍃
    - MongoDB NoSQL с админкой
    - Mongo Express внутренний порт: 8081
    - Includes: mongo-data volume

11. **Redis** 🔴
    - Redis кеш и очереди
    - Внутренний порт: 6379
    - Includes: redis-data volume

### CMS (3)

12. **WordPress** 📝
    - Популярная CMS + MySQL
    - Внутренний порт: 80
    - Includes: wordpress-data и db-data volumes

13. **Ghost** 👻
    - Современная платформа для блогов + MySQL
    - Внутренний порт: 2368
    - Includes: ghost-data и db-data volumes

14. **Strapi** 🚀
    - Headless CMS + PostgreSQL
    - Внутренний порт: 1337
    - Includes: strapi-data и db-data volumes

## Как использовать пресеты

### Через Web UI

1. Нажмите "New Project"
2. Выберите вкладку "From Preset"
3. Выберите категорию (All, Web, Backend, Database, CMS)
4. Кликните на нужный пресет
5. Заполните Project Name и Domain
6. Нажмите "Create"

**Примечание:** Порт указывать не нужно - Traefik автоматически настроит маршрутизацию по домену.

### Через API

```bash
# Получить список всех пресетов
curl http://localhost:8000/api/presets

# Получить пресеты по категории
curl http://localhost:8000/api/presets?category=web

# Получить детали пресета
curl http://localhost:8000/api/presets/nginx-static

# Создать проект из пресета
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-nginx-site",
    "domain": "example.com",
    "port": 8080,
    "compose_content": "<content from preset>",
    "env_vars": {}
  }'
```

## Структура пресета

Каждый пресет содержит:

```python
{
    "id": "nginx-static",
    "name": "Nginx Static Site",
    "description": "Простой статический сайт на Nginx",
    "category": "web",
    "icon": "🌐",
    "compose_content": "version: '3.8'...",
    "default_env_vars": {
        "PORT": "8080"
    },
    "default_port": 8080,
    "tags": ["nginx", "static", "simple"]
}
```

## Environment Variables

Каждый пресет может иметь предустановленные переменные окружения:

### Пример: WordPress

```
PORT=8080
DB_NAME=wordpress
DB_USER=wordpress
DB_PASSWORD=changeme123
DB_ROOT_PASSWORD=rootpass123
```

### Пример: PostgreSQL

```
POSTGRES_PORT=5432
POSTGRES_DB=mydb
POSTGRES_USER=admin
POSTGRES_PASSWORD=changeme123
PGADMIN_PORT=5050
PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=admin123
```

## Важные замечания

### 🔒 Безопасность

**ВСЕГДА меняйте пароли по умолчанию в production!**

Пресеты содержат слабые пароли для удобства разработки:
- `changeme123`
- `rootpass123`
- `admin123`

### 📁 Volumes

Многие пресеты создают Docker volumes для хранения данных:
- `postgres-data`
- `mysql-data`
- `mongo-data`
- `wordpress-data`
- `ghost-data`
- `strapi-data`

Эти volumes сохраняют данные даже после удаления контейнеров.

### 🔧 Кастомизация

После создания проекта из пресета, вы можете:
1. Редактировать docker-compose.yml через "Edit"
2. Добавлять/изменять env переменные
3. Добавлять новые сервисы
4. Изменять порты и volumes

## Добавление новых пресетов

Пресеты хранятся в коде: `backend/app/presets/`

Структура:
```
app/presets/
├── __init__.py        # Базовый класс Preset
├── web.py             # Web серверы
├── backend.py         # Backend фреймворки
├── databases.py       # Базы данных
├── cms.py             # CMS системы
└── registry.py        # Реестр всех пресетов
```

### Добавить новый пресет:

1. Откройте соответствующий файл (например, `web.py`)
2. Создайте новый объект `Preset`:

```python
MY_PRESET = Preset(
    id="my-preset",
    name="My Awesome Preset",
    description="Description here",
    category="web",
    icon="🎯",
    compose_content="""
version: '3.8'
services:
  app:
    image: my-image
    ports:
      - "${PORT}:80"
""",
    default_env_vars={"PORT": "8080"},
    default_port=8080,
    tags=["custom", "awesome"]
)
```

3. Добавьте в список: `WEB_PRESETS.append(MY_PRESET)`
4. Пересоберите контейнеры: `./rebuild.sh`

## API Endpoints

### GET /api/presets

Получить все пресеты или фильтровать по категории.

**Query Parameters:**
- `category` (optional): all, web, backend, database, cms

**Response:**
```json
[
  {
    "id": "nginx-static",
    "name": "Nginx Static Site",
    "description": "Простой статический сайт на Nginx",
    "category": "web",
    "icon": "🌐",
    "tags": ["nginx", "static", "simple"],
    "default_port": 8080
  }
]
```

### GET /api/presets/categories

Получить список категорий с количеством пресетов.

**Response:**
```json
[
  {"id": "all", "name": "All", "count": 14},
  {"id": "web", "name": "Web", "count": 3},
  {"id": "backend", "name": "Backend", "count": 4},
  {"id": "database", "name": "Database", "count": 4},
  {"id": "cms", "name": "CMS", "count": 3}
]
```

### GET /api/presets/{preset_id}

Получить полные детали пресета включая docker-compose content.

**Response:**
```json
{
  "id": "nginx-static",
  "name": "Nginx Static Site",
  "description": "Простой статический сайт на Nginx",
  "category": "web",
  "icon": "🌐",
  "compose_content": "version: '3.8'\n...",
  "default_env_vars": {"PORT": "8080"},
  "default_port": 8080,
  "tags": ["nginx", "static", "simple"]
}
```

## Примеры использования

### Быстрое создание Nginx сайта

1. Через UI: New Project → From Preset → Nginx Static Site
2. Name: `my-site`
3. Domain: `mysite.local`
4. Create

Проект будет создан с готовой конфигурацией!

### Быстрое создание WordPress

1. Through UI: New Project → From Preset → WordPress
2. Name: `my-blog`
3. Domain: `blog.example.com`
4. Env variables будут автоматически заполнены
5. Create

WordPress + MySQL будут готовы к использованию!

## Troubleshooting

### Пресеты не загружаются

```bash
# Проверить логи backend
docker-compose logs backend

# Перезапустить
./rebuild.sh
```

### Порт уже занят

При создании проекта, DockLite автоматически проверяет конфликты портов. Измените порт в форме если получаете ошибку.

### Volumes уже существуют

Если volume с таким именем уже существует:

```bash
# Посмотреть volumes
docker volume ls

# Удалить старый volume
docker volume rm postgres-data
```

---

**Количество пресетов**: 14  
**Категорий**: 4 (Web, Backend, Database, CMS)  
**Версия**: 1.0

