# Bash Completion for DockLite

Auto-completion система для DockLite CLI.

## Установка (10 секунд)

```bash
./docklite install-completion
source ~/.bashrc
```

Готово! ✅

---

## Что умеет

✅ **Автодополнение команд** - Tab показывает все команды  
✅ **Автодополнение опций** - Tab показывает доступные флаги  
✅ **Умное дополнение** - Tab дополняет имена сервисов, файлы бэкапов  
✅ **Частичное дополнение** - `st<TAB>` → показывает `start` и `status`  

---

## Примеры

### Показать все команды
```bash
./docklite <TAB><TAB>
```
Результат:
```
start       stop        restart     rebuild
logs        test        test-backend test-frontend
setup-user  setup-ssh   init-db
backup      restore     clean       status
version     help        install-completion
```

### Частичное дополнение
```bash
./docklite st<TAB>
```
Результат: показывает `start` и `status`

```bash
./docklite reb<TAB>
```
Результат: дополняет до `rebuild`

### Дополнение опций
```bash
./docklite start --<TAB><TAB>
```
Результат:
```
--build  --follow  --help
```

### Дополнение имен сервисов
```bash
./docklite logs <TAB><TAB>
```
Результат:
```
backend  frontend
```

### Дополнение файлов
```bash
./docklite restore <TAB>
```
Результат: показывает все `.tar.gz` файлы

```bash
./docklite backup -o <TAB>
```
Результат: показывает директории

---

## Удаление

```bash
./docklite install-completion --uninstall
source ~/.bashrc
```

---

## Глобальная установка

Для всех пользователей системы (требует root):

```bash
sudo ./docklite install-completion --global
```

Каждый пользователь должен перезагрузить shell:
```bash
source ~/.bashrc
```

---

## Технические детали

**Файл:** `scripts/completion/docklite-completion.bash`

**Функция:** `_docklite_completion`

**Регистрация:**
```bash
complete -F _docklite_completion ./docklite
complete -F _docklite_completion docklite
```

**Что дополняется:**
- 15+ команд
- 40+ опций
- Имена сервисов (backend, frontend)
- Файлы (*.tar.gz для restore)
- Директории (для backup -o)

---

## Troubleshooting

### Не работает после установки

```bash
# Перезагрузите shell
source ~/.bashrc

# Или перезапустите терминал
```

### Проверка установки

```bash
# Должна быть строка в ~/.bashrc
grep docklite ~/.bashrc

# Должна быть функция
type _docklite_completion

# Должна быть регистрация
complete -p ./docklite
```

### Работает в одном терминале, но не в другом

Каждый новый терминал автоматически загружает `~/.bashrc`. Если не работает, убедитесь что в ~/.bashrc нет `return` в начале файла (до source completion).

---

**Документация:** [scripts/completion/README.md](mdc:scripts/completion/README.md)  
**Основной CLI:** [SCRIPTS.md](mdc:SCRIPTS.md)
