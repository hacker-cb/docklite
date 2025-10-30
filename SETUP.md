# DockLite Development Setup

Quick start guide for setting up DockLite development environment.

## Requirements

- Python 3.8+ (with venv support)
- Docker Desktop (macOS) or Docker Engine (Linux)
- Git

## One-Command Setup

```bash
git clone https://github.com/hacker-cb/docklite.git
cd docklite
./docklite setup-dev
```

This automatically:
- ✅ Creates virtual environment (`.venv/`)
- ✅ Installs CLI dependencies (typer, rich, python-dotenv, PyYAML)
- ✅ Creates `.env` file from `.env.example`
- ✅ Verifies Docker is running
- ✅ Makes CLI executable

## What Gets Installed

### Virtual Environment (`.venv/`)
- **Isolated Python environment** - no system pollution
- **Auto-activated** by `./docklite` CLI - no manual activation needed
- **Cross-platform** - works on macOS, Linux, Windows

### CLI Dependencies
```
typer>=0.12.0       # Modern CLI framework
rich>=13.7.0        # Beautiful terminal output
python-dotenv>=1.0.0 # .env file support
PyYAML>=6.0         # Docker Compose parsing
```

## Next Steps

```bash
# 1. Edit configuration (set your HOSTNAME)
nano .env

# 2. Start DockLite
./docklite start

# 3. Create first admin user
./docklite add-user admin -p "YourPassword" --admin

# 4. Open in browser
# Frontend: http://your-domain.com
# API Docs: http://your-domain.com/docs
```

## Available Commands

```bash
./docklite --help          # Show all commands

# Development
./docklite start           # Start services
./docklite stop            # Stop services
./docklite restart         # Restart
./docklite rebuild         # Rebuild images
./docklite logs            # Show logs
./docklite test            # Run tests

# User Management
./docklite add-user <name> # Add user (interactive)
./docklite list-users      # List all users
./docklite reset-password  # Reset password

# Maintenance
./docklite status          # System status
./docklite backup          # Backup database
./docklite clean           # Clean unused resources
```

## Virtual Environment Details

### How It Works

The `./docklite` wrapper **automatically** uses `.venv/bin/python`:

```python
# You don't need to activate venv manually!
# The wrapper does this:
if venv_exists and not in_venv:
    exec(.venv/bin/python docklite)
```

### Manual venv Access (if needed)

```bash
# Activate manually (rarely needed)
source .venv/bin/activate

# Check what's installed
pip list

# Update dependencies
pip install -r scripts/requirements.txt

# Deactivate
deactivate
```

### macOS Homebrew Python

Works seamlessly! No need for `--break-system-packages` - venv isolates everything.

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'typer'`

**Solution:** Run `./docklite setup-dev` to create venv and install dependencies.

### Issue: `python3-venv is not installed`

**Solution (Linux):**
```bash
sudo apt-get install python3-venv
```

**Solution (macOS):**
```bash
# Python from Homebrew includes venv by default
brew install python@3.11
```

### Issue: Docker not running

**Solution (macOS):**
- Start Docker Desktop application

**Solution (Linux):**
```bash
sudo systemctl start docker
```

### Issue: Permission denied on `./docklite`

**Solution:**
```bash
chmod +x ./docklite
chmod +x ./scripts/docklite.sh
```

## Development Workflow

### Standard Flow

```bash
# One time
./docklite setup-dev

# Daily development
./docklite start          # Start containers
./docklite logs backend   # Watch backend logs
./docklite test           # Run tests after changes
./docklite stop           # Stop when done
```

### Backend Development (in Docker)

```bash
# Start
./docklite start

# Watch logs
docker compose logs -f backend

# Run tests
docker compose exec backend pytest -v

# Database migrations
docker compose exec backend alembic revision --autogenerate -m "description"
docker compose exec backend alembic upgrade head
```

### Frontend Development

```bash
# Install dependencies (once)
cd frontend && npm install

# Development server
npm run dev

# Tests
npm test

# Build
npm run build
```

### CLI Development (uses venv)

```bash
# CLI already uses .venv automatically
./docklite status

# If you need to modify CLI
cd scripts/
# Edit files in cli/
./docklite <command>  # Test changes
```

## Clean Install

```bash
# Remove everything
rm -rf .venv/
rm -f .env
docker compose down -v

# Start fresh
./docklite setup-dev
```

## CI/CD Notes

For GitHub Actions or other CI:

```yaml
# .github/workflows/ci.yml
- name: Setup DockLite
  run: |
    python3 -m venv .venv
    .venv/bin/pip install -r scripts/requirements.txt
    cp .env.example .env

- name: Test CLI
  run: ./docklite --version
```

## Production Deployment

**Note:** venv is for **development CLI only**. Production uses Docker containers.

```bash
# On production server
git clone <repo>
cd docklite

# Skip setup-dev on production!
# Just start containers:
docker compose up -d

# Create admin user via Docker
docker compose exec backend python create_user.py
```

## Links

- [README.md](./README.md) - Full documentation
- [scripts/README.md](./scripts/README.md) - CLI details
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [TRAEFIK.md](./TRAEFIK.md) - Reverse proxy guide

## Summary

✅ **One command setup:** `./docklite setup-dev`  
✅ **Auto venv activation:** No manual `source .venv/bin/activate`  
✅ **Cross-platform:** macOS, Linux, Windows  
✅ **Isolated dependencies:** No system pollution  
✅ **Development ready:** Start coding immediately  

Happy coding! 🚀

