# Быстрый старт DockLite

## Предварительные требования

- Ubuntu/Debian Linux
- Права sudo для установки Docker

## 1. Установить Docker

```bash
# Обновить пакеты
sudo apt update

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавить пользователя в группу docker
sudo usermod -aG docker $USER

# Перелогиниться или выполнить
newgrp docker
```

## 2. Запустить DockLite

```bash
cd /home/pavel/docklite
./start.sh
```

Подождите несколько минут, пока Docker соберет образы и запустит контейнеры.

## 3. Открыть в браузере

- **Frontend**: http://localhost:5173 или http://YOUR_SERVER_IP:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 4. Создать первый проект

1. Нажмите "New Project"
2. Заполните форму:
   - Name: `my-nginx-app`
   - Domain: `app.local`
   - Port: `8080`
   - Docker Compose Content:
   ```yaml
   version: '3.8'
   services:
     web:
       image: nginx:alpine
       ports:
         - "8080:80"
   ```
3. Нажмите "Create"

## 5. Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Только backend
docker-compose logs -f backend

# Только frontend
docker-compose logs -f frontend
```

## 6. Остановка

```bash
cd /home/pavel/docklite
./stop.sh
```

## Best Practices для bash скриптов

Все bash скрипты в проекте используют `set -e` для автоматической остановки при ошибках:

```bash
#!/bin/bash
set -e

# Ваш код здесь
```

## Полезные команды

```bash
# Перезапуск системы
docker-compose restart

# Пересборка после изменений
docker-compose up -d --build

# Статус контейнеров
docker-compose ps

# Войти в контейнер backend
docker exec -it docklite-backend sh

# Войти в контейнер frontend
docker exec -it docklite-frontend sh

# Проверить миграции БД
docker exec -it docklite-backend alembic current

# Применить миграции
docker exec -it docklite-backend alembic upgrade head
```

## Пересборка после изменений

```bash
cd /home/pavel/docklite
./rebuild.sh
```

## Доступ с внешнего IP

Система автоматически доступна по IP сервера:
- Frontend: http://YOUR_SERVER_IP:5173
- Backend API: http://YOUR_SERVER_IP:8000

Nginx внутри frontend контейнера автоматически проксирует `/api/*` запросы на backend.

## Troubleshooting

### Порты заняты

Если порты 8000 или 5173 заняты, измените их в `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Изменить с 8000 на 8001
  
  frontend:
    ports:
      - "5174:80"  # Изменить с 5173 на 5174
```

### Docker socket permission denied

```bash
sudo chmod 666 /var/run/docker.sock
# или
sudo usermod -aG docker $USER
newgrp docker
```

### Контейнеры не запускаются

```bash
# Проверить логи
docker-compose logs

# Пересобрать с нуля
docker-compose down -v
docker-compose up -d --build
```

## Что дальше?

- Прочитайте полный [README.md](./README.md)
- Изучите [STATUS.md](./STATUS.md) для понимания текущего состояния
- Посмотрите [FUTURE_IMPROVEMENTS.md](./FUTURE_IMPROVEMENTS.md) для планируемых функций
- Изучите API документацию: http://localhost:8000/docs

