# Python CLI - Quick Start Guide

**Status:** ✅ Production Ready  
**Tests:** 60/60 passing

---

## 🚀 Quick Start

### Installation (Already Done!)

```bash
# Dependencies installed:
sudo apt-get install python3-typer python3-rich python3-dotenv python3-pytest
```

### Basic Usage

```bash
# From project root
./docklite --help              # Show all commands
./docklite version             # Show version
./docklite status              # System status (beautiful Rich output!)
```

---

## 📋 Common Commands

### Development

```bash
./docklite start               # Start services
./docklite start --build       # Rebuild and start
./docklite stop                # Stop services
./docklite restart             # Restart (no logs)
./docklite logs                # Follow logs
./docklite logs backend        # Backend logs only
./docklite test                # Run all tests
```

### Maintenance

```bash
./docklite status              # Status with beautiful table
./docklite status --verbose    # Detailed status
./docklite list-users          # List all users
./docklite list-users --verbose # Users table (beautiful!)
./docklite reset-password admin # Reset password (interactive)
./docklite backup              # Backup system
```

### Deployment

```bash
sudo ./docklite setup-user     # Create system user
sudo ./docklite setup-ssh      # Configure SSH
./docklite init-db             # Initialize database
```

---

## ✨ New Features

### 1. Beautiful Output with Rich

**Status command:**
```
╭────────────────────────╮
│ DockLite System Status │
╰────────────────────────╯

✅ Traefik:  Running
✅ Backend:  Running
✅ Frontend: Running

▶ Access URLs (via Traefik):
ℹ Frontend:  http://artem.sokolov.me
ℹ Backend:   http://artem.sokolov.me/api
```

**List users verbose:**
```
                               Users                                
┏━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━┓
┃ ID ┃ Username ┃ Email             ┃ Role  ┃ Status ┃ System User ┃
┡━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━┩
│  1 │ admin    │ admin@example.com │ admin │ active │ docklite    │
└────┴──────────┴───────────────────┴───────┴────────┴─────────────┘
```

### 2. Auto-Completion (4 shells!)

```bash
# Install completion
./docklite --install-completion bash   # bash
./docklite --install-completion zsh    # zsh  
./docklite --install-completion fish   # fish
./docklite --install-completion pwsh   # PowerShell

# Reload shell
source ~/.bashrc

# Now enjoy auto-completion!
./docklite st<TAB>          # Completes to start/status
./docklite start --<TAB>    # Shows --build, --follow, --help
```

### 3. Better Help

```bash
# Auto-generated help for every command
./docklite --help              # All commands
./docklite start --help        # Start-specific options
./docklite backup --help       # Backup-specific options

# Rich formatting in help messages!
```

### 4. Type Safety

All commands have type hints:
```python
def start(
    build: bool = typer.Option(False, "--build"),  # Type checked!
    follow: bool = typer.Option(False, "--follow")
)
```

IDE knows types, provides autocomplete, catches errors!

---

## 🧪 Testing

### Run CLI Tests

```bash
cd /home/pavel/docklite/scripts

# All tests
python3 -m pytest tests/ -v    # Verbose (60 tests)
python3 -m pytest tests/ -q    # Quiet mode
python3 -m pytest tests/       # Normal mode

# Specific tests
python3 -m pytest tests/test_config.py -v
python3 -m pytest tests/test_commands_development.py -v

# Pattern matching
python3 -m pytest tests/ -k "test_status"
python3 -m pytest tests/ -k "test_list_users"
```

**Expected output:**
```
60 passed in 6.40s ✅
```

### Run All DockLite Tests

```bash
# From project root
./docklite test                # Backend (229) + Frontend (120+)
./docklite test-backend        # Backend only (229 tests)
./docklite test-frontend       # Frontend only (120+ tests)
```

---

## 🔧 Troubleshooting

### Command not found

```bash
# Ensure executable
chmod +x scripts/docklite

# Or use python3 directly
python3 scripts/docklite --help
```

### Module not found

```bash
# Install dependencies
sudo apt-get install python3-typer python3-rich python3-dotenv
```

### Permission denied (Docker)

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Then logout/login or use sg
sg docker -c "./docklite status"
```

### restart command shows logs

**Fixed!** `restart` now passes `follow=False` to start.

```bash
./docklite restart  # Should finish without hanging
```

---

## 📖 Documentation

**Main docs:**
- [PYTHON_CLI_FINAL_SUMMARY.md](mdc:PYTHON_CLI_FINAL_SUMMARY.md) - This comprehensive guide
- [CLI_MIGRATION_COMPLETE.md](mdc:CLI_MIGRATION_COMPLETE.md) - Migration details
- [scripts/README.md](mdc:scripts/README.md) - Script documentation

**Cursor Rules:**
- [.cursor/rules/python-cli.mdc](mdc:.cursor/rules/python-cli.mdc) - Python CLI patterns
- [.cursor/rules/scripts-cli.mdc](mdc:.cursor/rules/scripts-cli.mdc) - CLI conventions

**Code:**
- [scripts/cli/main.py](mdc:scripts/cli/main.py) - Main app
- [scripts/cli/config.py](mdc:scripts/cli/config.py) - Configuration
- [backend/app/cli_helpers/](mdc:backend/app/cli_helpers/) - Database helpers

---

## 💡 Tips

### Alias for Convenience

```bash
# Add to ~/.bashrc
alias dl='./docklite'

# Then use:
dl start
dl status
dl test
```

### Watch Mode for Development

```bash
# Frontend tests with watch
./docklite test-frontend --watch

# Backend tests for specific pattern
./docklite test-backend -k "test_traefik"
```

### Verbose Output

Most commands support `--verbose` or `-v`:
```bash
./docklite status --verbose     # More details
./docklite list-users --verbose # Table view
./docklite test --verbose       # Verbose test output
```

---

## 🎓 Learn More

### Understanding the Architecture

**Read in order:**
1. [scripts/cli/config.py](mdc:scripts/cli/config.py) - Start here
2. [scripts/cli/utils/console.py](mdc:scripts/cli/utils/console.py) - Logging
3. [scripts/cli/commands/development.py](mdc:scripts/cli/commands/development.py) - Commands
4. [backend/app/cli_helpers/list_users.py](mdc:backend/app/cli_helpers/list_users.py) - Helpers

### Adding New Commands

See [.cursor/rules/python-cli.mdc](mdc:.cursor/rules/python-cli.mdc) for:
- Command template
- Backend helper template
- Testing patterns
- Best practices

---

**Ready to use! Enjoy your modern Python CLI! 🎉**

