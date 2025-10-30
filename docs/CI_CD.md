# CI/CD Pipeline

## 🚀 GitHub Actions Workflows

DockLite использует GitHub Actions для автоматического тестирования и проверки качества кода.

---

## 📋 Workflows

### 1. Test Development Setup

**Файл:** `.github/workflows/test-setup-dev.yml`  
**Статус:** ![Setup Dev](https://github.com/hacker-cb/docklite/actions/workflows/test-setup-dev.yml/badge.svg)

#### Что проверяет

Автоматически тестирует процесс настройки окружения разработки на разных платформах:

✅ **Linux (Ubuntu Latest)**
- Создание `.venv/` виртуального окружения
- Установка зависимостей (typer, rich, dotenv, PyYAML)
- Создание `.env` файла
- Работа CLI команд
- Автоматическое использование venv

✅ **macOS (Latest)**
- Все проверки как для Linux
- Отсутствие загрязнения системного Python
- Проверка что НЕ используется `--break-system-packages`
- Чистота user site-packages

✅ **Множественные версии Python**
- Python 3.8 (минимальная)
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12 (latest)

#### Когда запускается

- ✅ Push в `main` или `dev` ветки
- ✅ Pull Request в `main` или `dev`
- ✅ Вручную через GitHub Actions UI
- ✅ При изменении:
  - `scripts/**`
  - `docklite` CLI wrapper
  - workflow файла

#### Проверки качества

```bash
# 1. Виртуальное окружение
✓ .venv/ создан
✓ .venv/bin/python существует
✓ Зависимости установлены в venv

# 2. Конфигурация
✓ .env файл создан из .env.example

# 3. CLI функциональность
✓ ./docklite version работает
✓ ./docklite --help работает
✓ CLI автоматически использует venv

# 4. Идемпотентность
✓ Повторный запуск setup-dev не ломает систему

# 5. Чистота системы (macOS)
✓ Нет пакетов в user site-packages
✓ Нет использования --user флагов
✓ Системный Python не загрязнен
```

#### Время выполнения

- **Linux:** ~2-3 минуты
- **macOS:** ~3-4 минуты  
- **Multiple Python:** ~8-10 минут (параллельно)

**Общее время:** ~4-5 минут

---

## 🔧 Как использовать

### Локальное тестирование

Перед пушем запустите те же проверки локально:

```bash
# 1. Очистите окружение
rm -rf .venv .env

# 2. Запустите setup
./docklite setup-dev

# 3. Проверьте зависимости
.venv/bin/python -c "import typer, rich, dotenv, yaml"

# 4. Проверьте CLI
./docklite version
./docklite --help

# 5. Проверьте идемпотентность
./docklite setup-dev  # должно пройти без ошибок

# 6. Проверьте чистоту системы (macOS)
python3 -m pip list --user | grep -E "(typer|rich)"
# Должно быть пусто!
```

### Запуск вручную в GitHub

1. Перейдите на: `https://github.com/<your-repo>/actions`
2. Выберите workflow: **"Test Development Setup"**
3. Нажмите: **"Run workflow"**
4. Выберите ветку
5. Подтвердите: **"Run workflow"**

### Просмотр результатов

```
✅ test-setup-linux          # Ubuntu tests passed
✅ test-setup-macos          # macOS tests passed  
✅ test-setup-multiple-python # Python 3.8-3.12 passed
✅ summary                    # All checks passed
```

---

## 🐛 Отладка ошибок

### ❌ ModuleNotFoundError в venv

**Причина:** Зависимости не установлены в venv

**Решение:**
```bash
# Проверьте requirements
cat scripts/requirements.txt

# Переустановите зависимости
.venv/bin/pip install -r scripts/requirements.txt

# Проверьте
.venv/bin/pip list
```

### ❌ CLI не использует venv

**Причина:** Ошибка в `docklite` wrapper

**Решение:**
```bash
# Проверьте wrapper
cat docklite | head -30

# Должен быть код auto-venv:
# if venv_path.exists():
#     venv_python = venv_path / "bin" / "python"
#     os.execv(str(venv_python), ...)
```

### ❌ Пакеты в user site-packages (macOS)

**Причина:** Использовался `--user` или `--break-system-packages`

**Решение:**
```bash
# Проверьте что флаги не используются
grep -r "\-\-user" scripts/
grep -r "break-system-packages" scripts/

# Очистите user packages
python3 -m pip uninstall --break-system-packages -y typer rich python-dotenv PyYAML
```

### ❌ .env не создан

**Причина:** Отсутствует `.env.example`

**Решение:**
```bash
# Проверьте шаблон
ls -la .env.example

# Создайте вручную
cp .env.example .env
```

---

## 📊 Метрики качества

### Coverage

- **Backend:** 95%+ (240 тестов)
- **Frontend:** 90%+ (120+ тестов)
- **CLI:** 80%+ (setup-dev workflow)

### Поддерживаемые платформы

| Платформа | Статус | Версии |
|-----------|--------|--------|
| Linux (Ubuntu) | ✅ Supported | Ubuntu Latest |
| macOS | ✅ Supported | macOS Latest |
| Windows | ⚠️ Partial | WSL2 only |

### Поддерживаемые версии Python

| Python | Статус | Примечание |
|--------|--------|------------|
| 3.8 | ✅ Supported | Минимальная версия |
| 3.9 | ✅ Supported | Полная поддержка |
| 3.10 | ✅ Supported | Полная поддержка |
| 3.11 | ✅ Supported | Рекомендуется |
| 3.12 | ✅ Supported | Latest |

---

## 🔐 Best Practices

### 1. Изолируйте зависимости

✅ **Правильно:**
```bash
./docklite setup-dev  # Создает venv автоматически
```

❌ **Неправильно:**
```bash
pip3 install --user typer rich  # Загрязняет систему
```

### 2. Проверяйте перед коммитом

```bash
# Запустите локальные проверки
./docklite setup-dev
./docklite version
./docklite test

# Только потом коммитьте
git add .
git commit -m "feat: ..."
git push
```

### 3. Следите за статусом CI

- Проверяйте бейджи в README
- Смотрите логи при ошибках
- Не мержите при красных тестах

### 4. Обновляйте workflow

При добавлении новых зависимостей:

```yaml
# Добавьте проверку в workflow
- name: Verify new dependency
  run: |
    .venv/bin/python -c "import new_package"
```

---

## 📚 Связанные документы

- [Development Setup Guide](../SETUP.md) - Руководство по настройке
- [CLI Documentation](../scripts/README.md) - Документация CLI
- [Contributing Guide](../CONTRIBUTING.md) - Гайд для контрибьюторов
- [Workflow README](.github/workflows/README.md) - Подробности о workflow

---

## 🎯 Roadmap

### Планируется добавить:

- [ ] Автоматическое развертывание (CD)
- [ ] Тестирование Docker setup
- [ ] Интеграционные тесты с реальным Docker
- [ ] Performance benchmarks
- [ ] Security scanning
- [ ] Dependency updates notifications

---

**Вопросы?** Создайте issue: `https://github.com/<your-repo>/issues`

**Автор:** DockLite Team  
**Обновлено:** 2024-10-30  
**Статус:** ✅ Production Ready

