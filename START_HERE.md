# 🚀 START HERE - DockLite Quick Setup

## Что это?

**DockLite** - система управления веб-сервером для деплоя множества проектов через docker-compose.

✅ **14 готовых пресетов** (Nginx, WordPress, Node.js, PostgreSQL и др.)  
✅ **Веб-интерфейс** для управления  
✅ **SSH деплой** - загрузка файлов через rsync/scp  
✅ **51 тест** с 85%+ coverage  

## 🏁 Быстрый старт (5 минут)

### Шаг 1: Установить Docker

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker
```

### Шаг 2: Настроить deployment

```bash
cd /home/pavel/docklite
sudo ./setup-docklite-user.sh
```

### Шаг 3: Запустить DockLite

```bash
./start.sh
```

### Шаг 4: Открыть в браузере

http://artem.sokolov.me:5173

**При первом открытии:**
1. Увидите экран "Initial Setup"
2. Создайте admin аккаунт (username, password)
3. Автоматически войдете в систему

### Шаг 5: Создать первый проект

1. Нажмите "New Project"
2. Выберите пресет (например, Nginx Static)
3. Заполните Name и Domain
4. Нажмите "Create"
5. Кликните иконку 📤 "Deploy Info" - получите команды для загрузки файлов

## 📋 Что дальше?

### Если нужен SSH доступ

```bash
# На вашем компьютере: скопировать ключ
cat ~/.ssh/id_ed25519.pub

# На сервере: добавить ключ
sudo -u docklite nano /home/docklite/.ssh/authorized_keys
```

### Примеры деплоя

```bash
# Загрузить файлы (Project ID = 1)
rsync -avz ./my-app/ docklite@artem.sokolov.me:/home/docklite/projects/1/

# Запустить контейнеры
ssh docklite@artem.sokolov.me "cd /home/docklite/projects/1 && docker-compose up -d"

# Посмотреть логи
ssh docklite@artem.sokolov.me "cd /home/docklite/projects/1 && docker-compose logs -f"
```

## 📖 Документация

| Для кого | Читайте |
|----------|---------|
| **Новичок** | [QUICKSTART.md](./QUICKSTART.md) |
| **Администратор** | [README.md](./README.md) |
| **Деплой** | [SSH_ACCESS.md](./SSH_ACCESS.md) |
| **Пресеты** | [PRESETS.md](./PRESETS.md) |
| **Тесты** | [TESTS.md](./TESTS.md) |
| **Обзор** | [FINAL_SUMMARY.md](./FINAL_SUMMARY.md) |

## 🛠️ Полезные команды

```bash
# Остановить
./stop.sh

# Перезапустить
./rebuild.sh

# Логи
docker-compose logs -f

# Тесты
./run-tests.sh

# Статус
docker-compose ps
```

## 📦 Что уже работает

✅ Создание проектов из пресетов  
✅ Редактирование docker-compose.yml  
✅ Управление .env переменными  
✅ SSH deployment с готовыми командами  
✅ Валидация конфигураций  
✅ 51 автоматический тест  

## 🔄 Что будет дальше

🔄 Авторизация (JWT)  
🔄 Управление контейнерами в UI  
🔄 Nginx virtual hosts  
🔄 SSL/HTTPS автоматически  
🔄 Просмотр логов в UI  
🔄 MCP для AI агентов  

## ⚡ Быстрые ссылки

- **UI**: http://artem.sokolov.me:5173
- **API**: http://artem.sokolov.me:8000
- **Docs**: http://artem.sokolov.me:8000/docs

## 🎯 Первый проект за 2 минуты

1. Откройте UI
2. "New Project" → From Preset → Nginx Static
3. Name: `test`, Domain: `test.local`
4. Create
5. Click 📤 "Deploy Info"
6. Copy команды и выполните

Готово! 🎉

---

**Если что-то не работает:**
1. Проверьте Docker: `docker --version`
2. Проверьте логи: `docker-compose logs`
3. См. [QUICKSTART.md](./QUICKSTART.md)

