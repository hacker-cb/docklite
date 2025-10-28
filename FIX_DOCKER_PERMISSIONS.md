# 🔧 Исправление прав доступа к Docker

## Проблема

Docker установлен, но пользователь `pavel` не имеет прав на Docker socket:

```
permission denied while trying to connect to the Docker daemon socket
```

## Решение

Выполните эти команды (требуется пароль sudo):

### Вариант 1: Добавить пользователя в группу docker (рекомендуется)

```bash
sudo usermod -aG docker pavel
newgrp docker
```

После этого:
```bash
# Проверить
docker ps

# Должно работать без ошибок!
```

### Вариант 2: Временно дать права на socket

```bash
sudo chmod 666 /var/run/docker.sock
```

**Внимание**: это менее безопасно, лучше использовать Вариант 1.

### Вариант 3: Перелогиниться

Если Вариант 1 не сработал сразу:

```bash
# Выйти из SSH сессии
exit

# Войти заново
ssh pavel@server

# Проверить группы
groups
# Должно быть: pavel sudo users docker

# Теперь Docker должен работать
docker ps
```

## После исправления

### 1. Проверить Docker

```bash
docker ps
docker --version
```

### 2. Запустить DockLite

```bash
cd /home/pavel/docklite
./start.sh
```

Или пересобрать:

```bash
./rebuild.sh
```

### 3. Запустить тесты

```bash
./run-tests.sh
```

## Ожидаемый результат

После исправления прав:

```bash
$ docker ps
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES

$ cd /home/pavel/docklite
$ ./start.sh
Starting DockLite...
Creating network "docklite_docklite-network" ... done
Creating docklite-backend  ... done
Creating docklite-frontend ... done

DockLite is starting...
Frontend: http://artem.sokolov.me:5173
Backend API: http://artem.sokolov.me:8000
```

## Если всё ещё не работает

### Проверить Docker daemon

```bash
systemctl status docker
```

Если не запущен:

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Проверить группу docker

```bash
groups pavel
```

Если нет docker:

```bash
sudo usermod -aG docker pavel
```

### Полный reset

```bash
# Остановить все
sudo systemctl stop docker

# Очистить socket
sudo rm /var/run/docker.sock

# Запустить заново
sudo systemctl start docker

# Добавить права
sudo usermod -aG docker pavel
newgrp docker
```

---

**После исправления продолжим с запуском тестов!** 🚀

