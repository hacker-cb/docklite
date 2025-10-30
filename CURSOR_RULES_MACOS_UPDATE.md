# Cursor Rules - macOS Compatibility Update

**Дата:** 2025-10-30  
**Статус:** ✅ Обновлено

## Что изменилось

### Новое правило: `macos-compatibility.mdc`

Создано новое правило `.cursor/rules/macos-compatibility.mdc` с полной документацией по кросс-платформенной разработке.

**Содержит:**
- ✅ Что работает на macOS
- ❌ Что не работает (Linux-only)
- 🔧 Паттерны написания кросс-платформенного кода
- 📋 Setup и workflow для macOS
- 🚀 Production deployment с macOS
- 🧪 Стратегия тестирования
- 🎯 Best practices и примеры

### Обновлено: `00-project-overview.mdc`

1. **Добавлена секция Platform Support:**
   ```
   Platform Support:
   - ✅ Development: macOS + Linux
   - ✅ Production: Linux
   - 🐳 Docker Desktop (macOS) or Docker Engine (Linux)
   ```

2. **Обновлены пути в Project Structure:**
   - Было: `/home/pavel/docklite/`
   - Стало: `<PROJECT_ROOT>/` (auto-detected)
   - Добавлена заметка: "Paths auto-detect based on script location. Works on macOS and Linux."

3. **Добавлена секция macOS Development:**
   - Ссылка на новое правило
   - Ключевые отличия
   - Что работает/не работает

4. **Обновлена секция Testing:**
   - Добавлен альтернативный способ через Docker Compose
   - Кросс-платформенные команды

## Ключевые правила для разработки

### 1. Автоопределение путей (ОБЯЗАТЕЛЬНО!)

**❌ НИКОГДА:**
```python
PROJECT_ROOT = Path("/home/pavel/docklite")
```

**✅ ВСЕГДА:**
```python
SCRIPTS_DIR = Path(__file__).parent.parent.absolute()
PROJECT_ROOT = SCRIPTS_DIR.parent
```

**Bash:**
```bash
get_project_root() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo "$(cd "$script_dir/../.." && pwd)"
}
```

### 2. Docker Group Detection

**✅ Правильно:**
```python
def has_docker_group() -> bool:
    # On macOS, docker group doesn't exist - skip sg
    if not shutil.which("sg"):
        return True  # macOS - no group switching needed
    
    # Linux logic...
```

**Bash:**
```bash
if command -v sg &> /dev/null && ! groups | grep -q docker; then
    sg docker -c "docker-compose up"
else
    docker-compose up  # macOS or in group
fi
```

### 3. Platform-Specific Commands

**Проверяй существование команд:**
```bash
if command -v hostnamectl &> /dev/null; then
    # Linux
else
    # macOS
fi
```

### 4. Linux-Only Functions

**Документируй и проверяй:**
```python
def create_system_user(username: str):
    """Create Linux system user (Linux only)."""
    if sys.platform != "linux":
        raise NotImplementedError("Requires Linux")
```

## Применение правил

### Когда применяются

**Автоматически применяются к:**
- `scripts/**/*.py` - Python CLI
- `scripts/**/*.sh` - Bash скрипты
- `backend/**/*.py` - Backend код

**Всегда применяется:**
- `00-project-overview.mdc` - base overview (alwaysApply: true)

### Как Cursor использует

Cursor автоматически:
1. Учитывает паттерны при генерации кода
2. Предлагает кросс-платформенные решения
3. Предупреждает о Linux-only функциях
4. Использует правильные пути

## Что изменилось в коде

### Изменённые файлы

1. **`scripts/cli/config.py`**
   - Автоопределение PROJECT_ROOT
   - Использование Path.home()

2. **`scripts/lib/common.sh`**
   - Автоопределение project root
   - Условное использование sg docker

3. **`scripts/cli/utils/docker.py`**
   - macOS detection в has_docker_group()
   - Пропуск sg на macOS

### Созданные файлы

1. **`.env`** (template)
   - Конфигурация для macOS
   - HOSTNAME=localhost
   - PROJECTS_DIR=/Users/pavel/...

2. **`MACOS_COMPATIBILITY.md`**
   - Полная документация
   - Setup инструкции
   - Troubleshooting

3. **`.cursor/rules/macos-compatibility.mdc`**
   - Правила для Cursor
   - Паттерны и примеры

## Проверка правил

Cursor автоматически загрузит обновлённые правила. Проверь:

```bash
# В Cursor попробуй создать новый скрипт
# Cursor должен предложить кросс-платформенный код

# Например, создай test.py с путями
# Cursor предложит Path(__file__) вместо хардкода
```

## Рекомендации

### Для новых фич

1. **Всегда используй auto-detect путей**
2. **Проверяй существование команд перед использованием**
3. **Документируй Linux-only функции**
4. **Тестируй на обеих платформах где возможно**

### Для code review

Проверяй:
- ❌ Нет хардкода путей
- ❌ Нет прямого использования `sg docker`
- ❌ Нет Linux-only команд без проверки
- ✅ Используется Path.home()
- ✅ Есть проверка command existence

## Дополнительная документация

- **Правила:** `.cursor/rules/macos-compatibility.mdc`
- **Гайд:** `MACOS_COMPATIBILITY.md`
- **Overview:** `.cursor/rules/00-project-overview.mdc`

## Итог

✅ Все правила обновлены для кросс-платформенной разработки  
✅ Cursor будет предлагать правильные паттерны  
✅ Код работает на macOS и Linux  
✅ Документация полная и актуальная  

---

**Следующие шаги:**
1. Перезагрузи Cursor (если нужно)
2. Попробуй создать новый код - правила применятся автоматически
3. При code review используй правила как checklist

