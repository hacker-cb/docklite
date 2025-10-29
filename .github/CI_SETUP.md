# CI Setup для DockLite

## ✅ Что настроено

### Основной workflow: `ci.yml`

**Запускается при:**
- Push в `master` или `dev`
- Pull Request к `master` или `dev`

**Проверяет (параллельно):**

1. **Backend:**
   - Flake8 linting (синтаксис + сложность)
   - Black formatting
   - Pytest tests (all)

2. **Frontend:**
   - ESLint linting
   - Vitest tests (all)

3. **Docker (после тестов):**
   - Backend image build
   - Frontend image build

**Время:** ~8-10 минут

**Оптимизации:**
- ✅ Parallel jobs
- ✅ Pip/NPM cache
- ✅ Docker layer cache
- ✅ Fail fast strategy

---

## 🚀 Использование

```bash
# 1. Commit workflows
git add .github/
git commit -m "ci: add GitHub Actions"

# 2. Push в master
git push origin master

# 3. Проверьте результат
https://github.com/hacker-cb/docklite/actions
```

---

## 📊 Badge

Добавлен в README.md:

```markdown
![CI](https://github.com/hacker-cb/docklite/workflows/CI/badge.svg)
```

---

## 💡 Локальная проверка перед push

```bash
# Backend
cd backend
flake8 app
black --check app
pytest

# Frontend  
cd frontend
npm run lint
npm test

# Docker
docker compose build
```

---

**Готово!** CI будет автоматически проверять каждый push и PR. 🚀

