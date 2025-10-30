# 🚀 Как задеплоить ваш проект

## Проект создан! Что дальше?

Ваш проект создан с ID: `{project_id}` и доменом: `{domain}`

Директория на сервере: `/home/docklite/projects/{project_id}/`

## Быстрый старт

### 1. Загрузите ваши файлы

**Через rsync (рекомендуется):**
```bash
rsync -avz ./your-app/ docklite@{server}:/home/docklite/projects/{project_id}/
```

**Через scp:**
```bash
scp -r ./your-app/* docklite@{server}:/home/docklite/projects/{project_id}/
```

**Через SFTP/FileZilla:**
- Host: `{server}`
- User: `docklite`
- Protocol: SFTP
- Path: `/home/docklite/projects/{project_id}/`

### 2. Запустите docker-compose

```bash
ssh docklite@{server} "cd /home/docklite/projects/{project_id} && docker-compose up -d"
```

### 3. Проверьте статус

```bash
ssh docklite@{server} "cd /home/docklite/projects/{project_id} && docker-compose ps"
```

## Нужна помощь?

### Настройка SSH (первый раз)

Если у вас еще нет SSH доступа:

1. **Сгенерируйте SSH ключ** (на вашем компьютере):
   ```bash
   ssh-keygen -t ed25519
   cat ~/.ssh/id_ed25519.pub
   ```

2. **Отправьте публичный ключ** администратору сервера

3. **Проверьте доступ**:
   ```bash
   ssh docklite@{server}
   ```

### Структура файлов

Ваш `docker-compose.yml` уже создан в проекте. Добавьте туда файлы вашего приложения.

**Пример структуры:**
```
/home/docklite/projects/{project_id}/
├── docker-compose.yml   (создан автоматически)
├── .env                 (если есть переменные)
├── app/                 (ваше приложение)
│   ├── index.js
│   ├── package.json
│   └── ...
└── nginx.conf          (если нужен)
```

### Примеры

#### Node.js приложение
```bash
# Загрузить код
rsync -avz --exclude 'node_modules' ./ docklite@{server}:/home/docklite/projects/{project_id}/

# Запустить
ssh docklite@{server} "cd /home/docklite/projects/{project_id} && docker-compose up -d"
```

#### Static HTML сайт
```bash
# Загрузить HTML файлы в папку html/
rsync -avz ./html/ docklite@{server}:/home/docklite/projects/{project_id}/html/

# Перезапустить nginx
ssh docklite@{server} "cd /home/docklite/projects/{project_id} && docker-compose restart"
```

## Полезные команды

```bash
# Просмотр логов
ssh docklite@{server} "cd /home/docklite/projects/{project_id} && docker-compose logs -f"

# Перезапуск
ssh docklite@{server} "cd /home/docklite/projects/{project_id} && docker-compose restart"

# Остановка
ssh docklite@{server} "cd /home/docklite/projects/{project_id} && docker-compose down"

# Обновление кода
rsync -avz ./app/ docklite@{server}:/home/docklite/projects/{project_id}/
ssh docklite@{server} "cd /home/docklite/projects/{project_id} && docker-compose restart"
```

## 📖 Полная документация

См. [SSH_ACCESS.md](./SSH_ACCESS.md) для подробной информации.

---

**Домен**: `{domain}`  
**Project ID**: `{project_id}`  
**Server**: `{server}`

