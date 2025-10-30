# SSH/SFTP доступ к проектам DockLite

## 📋 Обзор

DockLite использует отдельного системного пользователя для деплоя проектов:
- **Пользователь**: `docklite` (настраиваемый)
- **Директория проектов**: `/home/docklite/projects/`
- **Доступ**: SSH/SFTP/rsync

## 🚀 Быстрый старт

### 1. Настройка сервера (один раз)

```bash
cd ~/docklite
sudo ./setup-docklite-user.sh
```

Это создаст:
- Пользователя `docklite`
- Директорию `/home/docklite/projects/`
- SSH конфигурацию

### 2. Добавление SSH ключа

```bash
# На вашем компьютере: сгенерировать ключ (если нет)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Скопировать публичный ключ
cat ~/.ssh/id_ed25519.pub

# На сервере: добавить ключ
sudo -u docklite nano /home/docklite/.ssh/authorized_keys
# Вставить публичный ключ и сохранить
```

### 3. Проверка доступа

```bash
ssh docklite@your-server-ip
```

## 📤 Методы деплоя

### Метод 1: rsync (рекомендуется)

**Преимущества**: быстрый, инкрементальный, удаляет старые файлы

```bash
# Синхронизация локальной папки с проектом на сервере
rsync -avz --delete \
  ./my-app/ \
  docklite@server:/home/docklite/projects/{project_id}/

# С прогресс-баром
rsync -avz --delete --progress \
  ./my-app/ \
  docklite@server:/home/docklite/projects/{project_id}/

# Исключить определенные файлы
rsync -avz --delete \
  --exclude 'node_modules' \
  --exclude '.git' \
  --exclude '.env.local' \
  ./my-app/ \
  docklite@server:/home/docklite/projects/{project_id}/
```

### Метод 2: scp (простой)

**Преимущества**: простой, знакомый

```bash
# Копировать файл
scp app.js docklite@server:/home/docklite/projects/{project_id}/

# Копировать директорию
scp -r ./my-app/ docklite@server:/home/docklite/projects/{project_id}/

# Несколько файлов
scp index.html style.css main.js \
  docklite@server:/home/docklite/projects/{project_id}/
```

### Метод 3: SFTP (интерактивный)

**Преимущества**: интерактивный, GUI клиенты (FileZilla, Cyberduck)

```bash
# Командная строка
sftp docklite@server
cd /home/docklite/projects/{project_id}
put -r my-app/
quit

# Или через GUI:
# Host: your-server-ip
# Protocol: SFTP
# User: docklite
# Port: 22
# Auth: SSH key
```

### Метод 4: Git + SSH

```bash
# На сервере: клонировать репозиторий
ssh docklite@server
cd /home/docklite/projects/{project_id}
git clone https://github.com/user/repo.git .

# Обновление
ssh docklite@server "cd /home/docklite/projects/{project_id} && git pull"
```

## 🐳 Запуск после деплоя

После загрузки файлов, запустить docker-compose:

```bash
# Способ 1: SSH команда
ssh docklite@server \
  "cd /home/docklite/projects/{project_id} && docker-compose up -d"

# Способ 2: Интерактивная сессия
ssh docklite@server
cd /home/docklite/projects/{project_id}
docker-compose up -d
exit

# Способ 3: Перезапуск
ssh docklite@server \
  "cd /home/docklite/projects/{project_id} && docker-compose restart"
```

## 📝 Полный пример деплоя

### Пример: Node.js приложение

```bash
# 1. Создать проект в DockLite UI
#    Project ID: 5
#    Domain: myapp.example.com

# 2. Подготовить приложение локально
cd ~/my-nodejs-app
npm install
npm run build  # если нужна сборка

# 3. Загрузить на сервер
rsync -avz --delete \
  --exclude 'node_modules' \
  --exclude '.git' \
  ./ \
  docklite@server:/home/docklite/projects/5/

# 4. Запустить на сервере
ssh docklite@server \
  "cd /home/docklite/projects/5 && docker-compose up -d"

# 5. Проверить логи
ssh docklite@server \
  "cd /home/docklite/projects/5 && docker-compose logs -f"
```

### Пример: Static HTML сайт

```bash
# 1. Создать проект с Nginx пресетом
#    Project ID: 3
#    Domain: site.example.com

# 2. Создать html папку локально
mkdir html
echo "<h1>Hello World</h1>" > html/index.html

# 3. Загрузить
rsync -avz ./html/ docklite@server:/home/docklite/projects/3/html/

# 4. Перезапустить nginx
ssh docklite@server \
  "cd /home/docklite/projects/3 && docker-compose restart"

# Готово! Сайт доступен на http://site.example.com
```

## 🔐 Безопасность

### Ограничение доступа к своим проектам

По умолчанию пользователь `docklite` имеет доступ ко всем проектам. Для ограничения:

```bash
# На сервере: установить права только на свой проект
sudo chown -R docklite:docklite /home/docklite/projects/{project_id}
sudo chmod 700 /home/docklite/projects/{project_id}
```

### Использование SSH config

На локальном компьютере создайте `~/.ssh/config`:

```
Host docklite
    HostName your-server-ip
    User docklite
    IdentityFile ~/.ssh/id_ed25519
    Port 22
```

Теперь можно использовать короткий алиас:

```bash
rsync -avz ./app/ docklite:/home/docklite/projects/5/
ssh docklite "cd /home/docklite/projects/5 && docker-compose up -d"
```

### Отключение password аутентификации

Для безопасности отключите пароли, оставьте только SSH keys:

```bash
# На сервере
sudo nano /etc/ssh/sshd_config

# Найти и изменить:
PasswordAuthentication no
PubkeyAuthentication yes

# Перезапустить SSH
sudo systemctl restart sshd
```

## 🛠️ Автоматизация

### Bash скрипт для деплоя

Создайте `deploy.sh` в вашем проекте:

```bash
#!/bin/bash
set -e

PROJECT_ID=5
SERVER=docklite@your-server
REMOTE_PATH=/home/docklite/projects/$PROJECT_ID

echo "🚀 Deploying to $SERVER..."

# Build (если нужно)
echo "📦 Building..."
npm run build

# Upload
echo "📤 Uploading..."
rsync -avz --delete \
  --exclude 'node_modules' \
  --exclude '.git' \
  --exclude '*.log' \
  ./ $SERVER:$REMOTE_PATH/

# Restart
echo "🔄 Restarting..."
ssh $SERVER "cd $REMOTE_PATH && docker-compose up -d"

echo "✅ Deployed successfully!"
```

Использование:

```bash
chmod +x deploy.sh
./deploy.sh
```

### Makefile

```makefile
PROJECT_ID = 5
SERVER = docklite@your-server
REMOTE_PATH = /home/docklite/projects/$(PROJECT_ID)

.PHONY: deploy logs restart

deploy:
	@echo "🚀 Deploying..."
	rsync -avz --delete \
		--exclude 'node_modules' \
		./ $(SERVER):$(REMOTE_PATH)/
	ssh $(SERVER) "cd $(REMOTE_PATH) && docker-compose up -d"
	@echo "✅ Done!"

logs:
	ssh $(SERVER) "cd $(REMOTE_PATH) && docker-compose logs -f"

restart:
	ssh $(SERVER) "cd $(REMOTE_PATH) && docker-compose restart"
```

Использование:

```bash
make deploy
make logs
make restart
```

## 📊 Где узнать Project ID?

После создания проекта в DockLite UI:

1. **В таблице проектов** - колонка "ID"
2. **В URL**: `/api/projects/{id}`
3. **Через API**:
   ```bash
   curl http://server:8000/api/projects
   ```

## 🔍 Troubleshooting

### Permission denied

```bash
# Проверить права на проект
ls -la /home/docklite/projects/

# Исправить владельца
sudo chown -R docklite:docklite /home/docklite/projects/{project_id}
```

### SSH connection refused

```bash
# Проверить SSH сервис
sudo systemctl status sshd

# Проверить firewall
sudo ufw status
sudo ufw allow 22/tcp
```

### Docker permission denied

```bash
# Добавить docklite в группу docker
sudo usermod -a -G docker docklite

# Перелогиниться
```

### rsync: command not found

```bash
# Установить rsync
sudo apt install rsync
```

## 📖 Дополнительные ресурсы

- [rsync документация](https://linux.die.net/man/1/rsync)
- [SSH best practices](https://www.ssh.com/academy/ssh/config)
- [Docker Compose документация](https://docs.docker.com/compose/)

## 🎯 Best Practices

1. **Всегда используйте SSH keys**, не пароли
2. **Добавьте .rsyncignore** для исключения ненужных файлов
3. **Делайте backup** перед обновлением
4. **Тестируйте локально** перед деплоем
5. **Используйте git tags** для версионирования
6. **Мониторьте логи** после деплоя
7. **Автоматизируйте** через скрипты

## 🔄 Обновление проекта

```bash
# 1. Остановить контейнеры
ssh docklite@server "cd /home/docklite/projects/5 && docker-compose down"

# 2. Обновить файлы
rsync -avz ./new-version/ docklite@server:/home/docklite/projects/5/

# 3. Запустить заново
ssh docklite@server "cd /home/docklite/projects/5 && docker-compose up -d"
```

## 📞 Поддержка

Если у вас проблемы с SSH доступом:
1. Проверьте логи: `sudo journalctl -u sshd -f`
2. Проверьте права: `ls -la /home/docklite/`
3. Проверьте ключи: `cat /home/docklite/.ssh/authorized_keys`

