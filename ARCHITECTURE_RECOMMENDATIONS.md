# Architecture Recommendations для стабильности и расширяемости

**Для:** DockLite - стабильный расширяемый проект  
**Дата:** 2025-10-29

---

## 🚨 КРИТИЧНО (must-fix перед production)

### 1. CORS Security ⚠️ HIGH PRIORITY

**Проблема:**
```python
# backend/app/main.py:15
allow_origins=["*"]  # НЕБЕЗОПАСНО!
```

**Риск:**
- XSS attacks
- CSRF attacks
- Любой сайт может делать requests к вашему API

**Решение:**
```python
# backend/app/core/config.py
CORS_ORIGINS: list = ["http://localhost", "http://artem.sokolov.me"]

# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Только доверенные домены
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

### 2. Rate Limiting

**Проблема:**
- Нет защиты от DDoS
- Login endpoint уязвим к brute-force
- API может быть перегружен

**Решение:**
```bash
# requirements.txt
slowapi==0.1.9
```

```python
# backend/app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# backend/app/api/auth.py
@limiter.limit("5/minute")  # Только 5 попыток входа в минуту
@router.post("/auth/login")
async def login(...):
```

---

### 3. Environment Variables Validation

**Проблема:**
- Нет проверки обязательных переменных
- При отсутствии SECRET_KEY приложение упадет после старта

**Решение:**
```python
# backend/app/core/config.py
from pydantic import field_validator

class Settings(BaseSettings):
    SECRET_KEY: str
    
    @field_validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters')
        return v
    
    @field_validator('DATABASE_URL')
    def validate_database(cls, v):
        if 'sqlite' in v and not v.startswith('sqlite+aiosqlite'):
            raise ValueError('Use sqlite+aiosqlite:// for async support')
        return v
```

---

### 4. Database Backups Automation

**Проблема:**
- Нет автоматических backups
- При ошибке миграции данные могут быть потеряны

**Решение:**
```bash
# scripts/maintenance/backup.sh
#!/bin/bash
# Автоматический backup каждый день в 3:00
# Добавить в crontab:
# 0 3 * * * /opt/docklite/scripts/maintenance/backup.sh

# Также: backup перед каждой миграцией
./docklite backup
alembic upgrade head
```

---

### 5. Graceful Shutdown

**Проблема:**
- При рестарте активные requests обрываются
- Нет cleanup ресурсов

**Решение:**
```python
# backend/app/main.py
import signal
import asyncio

shutdown_event = asyncio.Event()

@app.on_event("startup")
async def setup_signals():
    loop = asyncio.get_event_loop()
    
    def handle_shutdown(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        shutdown_event.set()
    
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

@app.on_event("shutdown")
async def shutdown():
    logger.info("Closing database connections...")
    await engine.dispose()
    logger.info("Shutdown complete")
```

---

## 💡 ВАЖНО для расширяемости

### 6. API Versioning

**Зачем:**
- Breaking changes в будущем
- Поддержка старых клиентов
- Постепенная миграция

**Как:**
```python
# Вариант 1: URL versioning (рекомендуется)
app.include_router(projects.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")

# Вариант 2: Header versioning
@app.middleware("http")
async def version_middleware(request, call_next):
    api_version = request.headers.get("API-Version", "v1")
    request.state.api_version = api_version
    return await call_next(request)
```

---

### 7. Database Connection Pooling

**Оптимизация:**
```python
# backend/app/core/database.py
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=20,              # Максимум 20 соединений
    max_overflow=10,           # +10 при пиковых нагрузках
    pool_timeout=30,           # Timeout ожидания соединения
    pool_recycle=3600,         # Переподключение каждый час
    pool_pre_ping=True,        # Проверка соединения перед использованием
)
```

---

### 8. Caching Strategy

**Для производительности:**
```python
# Option 1: In-memory cache (простой)
from functools import lru_cache

@lru_cache(maxsize=100)
def get_presets_cached():
    return get_presets()

# Option 2: Redis (production)
# requirements.txt
redis==5.0.0
aioredis==2.0.1

# backend/app/core/cache.py
import aioredis

redis_client = await aioredis.from_url(
    "redis://localhost",
    encoding="utf-8",
    decode_responses=True
)

# Кэшировать presets, users list
```

---

### 9. Request ID Tracking

**Для debugging:**
```python
# backend/app/middleware/request_id.py
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

# Использование в логах
logger.info(f"[{request.state.request_id}] Processing request...")
```

---

### 10. Structured Error Responses

**Стандартизация:**
```python
# backend/app/models/errors.py
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None
    request_id: Optional[str] = None
    timestamp: datetime = datetime.utcnow()

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message=str(exc),
            request_id=getattr(request.state, "request_id", None)
        ).dict()
    )
```

---

## 🎯 Приоритеты для стабильности

### Немедленно (перед production):

1. **Fix CORS** (5 минут) - критично для безопасности
2. **Add rate limiting** (15 минут) - защита от атак
3. **Environment validation** (10 минут) - предотвращение ошибок запуска

### Скоро (в течение недели):

4. **Database backups automation** (30 минут)
5. **Graceful shutdown** (20 минут)
6. **Error tracking** (Sentry) (30 минут)

### Средний срок (в течение месяца):

7. **API versioning** (1 час)
8. **Connection pooling optimization** (30 минут)
9. **Caching strategy** (2 часа)
10. **Request ID tracking** (30 минут)

---

## 📋 Чеклист для production-ready проекта

### Security ✅/⚠️
- ✅ JWT authentication
- ✅ Password hashing (bcrypt)
- ✅ SQL injection protection (ORM)
- ✅ Role-based access
- ⚠️ CORS (fix needed!)
- ⚠️ Rate limiting (нет!)
- ✅ Input validation

### Reliability
- ✅ CI/CD pipeline
- ✅ 240+ tests
- ✅ Error handling
- ⚠️ Graceful shutdown (нет!)
- ⚠️ Database backups (manual only)
- ✅ Health checks

### Scalability
- ✅ Async architecture
- ⚠️ Connection pooling (default settings)
- ⚠️ Caching (нет!)
- ✅ Modular design

### Observability
- ✅ Logging
- ⚠️ Error tracking (нет!)
- ⚠️ Metrics (нет!)
- ✅ Health endpoint
- ⚠️ Request tracing (нет!)

### Maintainability
- ✅ Clean architecture
- ✅ Type hints
- ✅ Documentation
- ✅ Pre-commit hooks
- ✅ Linting & formatting

---

## 🚀 Рекомендуемый план действий

### Phase 1: Критичная безопасность (сегодня)
```bash
1. Fix CORS configuration
2. Add rate limiting
3. Validate environment variables
```

### Phase 2: Операционная стабильность (эта неделя)
```bash
4. Setup automated backups
5. Add graceful shutdown
6. Configure Sentry for error tracking
```

### Phase 3: Производительность (следующая неделя)
```bash
7. Optimize connection pooling
8. Add caching for presets/users
9. Add request ID tracking
```

### Phase 4: Расширяемость (этот месяц)
```bash
10. API versioning (/api/v1)
11. Pagination for lists
12. Metrics endpoint
13. Audit logging
```

---

## 💡 Ключевые принципы для расширяемости

1. **Separation of Concerns** ✅ (уже есть)
   - API, Services, Models разделены

2. **Dependency Injection** ✅ (FastAPI Depends)
   - Легко мокировать и тестировать

3. **Configuration over Code** ⚠️ (частично)
   - Нужно больше через .env

4. **Fail Fast** ✅ (validation)
   - Pydantic схемы

5. **Backward Compatibility**⚠️ (нет версионирования)
   - Добавить API versioning

6. **Idempotency** ⚠️ (частично)
   - Некоторые операции не idempotent

7. **Observability** ⚠️ (базовая)
   - Нужны metrics и tracing

8. **Modularity** ✅ (отлично)
   - Можно добавлять новые API modules

---

## 📚 Дополнительно

### Документация API
- ✅ OpenAPI/Swagger (/docs)
- Добавить: примеры requests/responses
- Добавить: authentication guide для API

### Dependency Management
- ✅ requirements.txt
- Рассмотреть: poetry/pipenv для lock файлов
- Добавить: dependabot для автообновлений

### Configuration
- Добавить: config validation при старте
- Добавить: разные configs для dev/staging/prod
- Добавить: secrets management (не в .env)

---

**Проект в отличном состоянии!** Основные улучшения - CORS, rate limiting, и backups. Остальное - для масштабирования. 🚀

