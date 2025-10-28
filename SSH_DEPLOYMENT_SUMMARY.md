# ✅ SSH Deployment - Реализовано

**Дата**: 28 октября 2025

## Что сделано

### 1. Системный пользователь для деплоя

**Пользователь**: `docklite` (настраиваемый через переменную)
**Директория**: `/home/docklite/projects/`

### 2. Скрипт автоматической настройки

**setup-docklite-user.sh**
- ✅ Создает пользователя `docklite`
- ✅ Создает директорию `/home/docklite/projects/`
- ✅ Настраивает SSH доступ (`.ssh/authorized_keys`)
- ✅ Обновляет `.env` с новыми путями
- ✅ Настраивает права доступа
- ✅ Добавляет пользователя в группу docker

### 3. Документация

**SSH_ACCESS.md** (полный гайд, 400+ строк)
- 📖 Обзор архитектуры
- 🚀 Быстрый старт
- 📤 4 метода деплоя (rsync, scp, SFTP, Git)
- 🐳 Запуск docker-compose
- 📝 Полные примеры (Node.js, Static HTML)
- 🔐 Безопасность
- 🛠️ Автоматизация (bash, Makefile)
- 🔍 Troubleshooting

**DEPLOY_GUIDE.md** (краткий гайд для пользователей)
- Быстрый старт для новых проектов
- Настройка SSH первый раз
- Примеры команд
- Структура файлов

### 4. Конфигурация

**docker-compose.yml**
- ✅ Использует переменную `PROJECTS_DIR`
- ✅ Использует переменную `DEPLOY_USER`
- ✅ Default: `/home/docklite/projects`

**.env.example**
- ✅ `PROJECTS_DIR=/home/docklite/projects`
- ✅ `DEPLOY_USER=docklite`

## Как использовать

### Для администратора сервера

1. **Запустить setup скрипт**:
```bash
cd /home/pavel/docklite
sudo ./setup-docklite-user.sh
```

2. **Добавить SSH ключи пользователей**:
```bash
sudo -u docklite nano /home/docklite/.ssh/authorized_keys
```

3. **Перезапустить DockLite**:
```bash
./rebuild.sh
```

### Для пользователей

1. **Создать проект через UI**
   - Получить Project ID

2. **Загрузить файлы**:
```bash
rsync -avz ./app/ docklite@server:/home/docklite/projects/{id}/
```

3. **Запустить**:
```bash
ssh docklite@server "cd /home/docklite/projects/{id} && docker-compose up -d"
```

## Методы деплоя

| Метод | Команда | Преимущества |
|-------|---------|--------------|
| **rsync** | `rsync -avz ./app/ docklite@server:/path/` | Инкрементальный, быстрый |
| **scp** | `scp -r ./app/ docklite@server:/path/` | Простой, знакомый |
| **SFTP** | `sftp docklite@server` | Интерактивный, GUI |
| **Git** | `git clone/pull` | Version control |

## Безопасность

- ✅ Только SSH keys (не пароли)
- ✅ Отдельный пользователь для деплоя
- ✅ Доступ только к `/home/docklite/projects/`
- ✅ В группе docker для управления контейнерами
- ⚠️ TODO: chroot jail для изоляции (Фаза 2+)
- ⚠️ TODO: ограничение доступа к конкретным проектам (Фаза 2+)

## Конфигурация

### Изменить пользователя

```bash
# В .env
DEPLOY_USER=myuser
PROJECTS_DIR=/home/myuser/projects

# Запустить setup
sudo DEPLOY_USER=myuser ./setup-docklite-user.sh

# Пересобрать
./rebuild.sh
```

### Изменить директорию проектов

```bash
# В .env
PROJECTS_DIR=/var/www/projects

# Создать директорию
sudo mkdir -p /var/www/projects
sudo chown docklite:docklite /var/www/projects

# Пересобрать
./rebuild.sh
```

## Примеры использования

### Деплой Node.js приложения

```bash
# 1. Создать проект в UI (ID=5, preset: Node.js)

# 2. Загрузить код
rsync -avz --exclude 'node_modules' ./ docklite@server:/home/docklite/projects/5/

# 3. Запустить
ssh docklite@server "cd /home/docklite/projects/5 && docker-compose up -d"

# 4. Проверить логи
ssh docklite@server "cd /home/docklite/projects/5 && docker-compose logs -f"
```

### Деплой static сайта

```bash
# 1. Создать проект (ID=3, preset: Nginx Static)

# 2. Загрузить HTML
rsync -avz ./html/ docklite@server:/home/docklite/projects/3/html/

# 3. Перезапустить
ssh docklite@server "cd /home/docklite/projects/3 && docker-compose restart"
```

### Автоматизированный деплой

Создать `deploy.sh`:
```bash
#!/bin/bash
set -e

PROJECT_ID=5
rsync -avz ./ docklite@server:/home/docklite/projects/$PROJECT_ID/
ssh docklite@server "cd /home/docklite/projects/$PROJECT_ID && docker-compose up -d"
```

## Файлы

```
/home/pavel/docklite/
├── setup-docklite-user.sh       # Скрипт настройки
├── SSH_ACCESS.md                 # Полная документация
├── DEPLOY_GUIDE.md               # Краткий гайд
├── SSH_DEPLOYMENT_SUMMARY.md     # Этот файл
├── .env.example                  # Обновлен
└── docker-compose.yml            # Обновлен
```

## TODO (будущие улучшения)

### Ближайшее
- [ ] UI: показывать deployment инструкции после создания проекта
- [ ] API: endpoint для получения deploy команд
- [ ] Webhook для GitHub/GitLab автодеплоя

### Долгосрочное
- [ ] Web-based file manager
- [ ] Built-in git integration
- [ ] CLI tool (`docklite deploy`)
- [ ] Per-project SSH users (chroot)
- [ ] SFTP-only режим (без shell)

## Связанные документы

- [SSH_ACCESS.md](./SSH_ACCESS.md) - Полная документация по SSH
- [DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md) - Краткий гайд для пользователей
- [README.md](./README.md) - Основная документация DockLite

---

**Статус**: ✅ Полностью реализовано и готово к использованию

