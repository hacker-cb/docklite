# DockLite Scripts - Quick Reference

Production-grade CLI for managing DockLite.

## Quick Commands

```bash
# System management
./docklite start            # Start DockLite
./docklite stop             # Stop DockLite
./docklite restart          # Restart
./docklite rebuild          # Rebuild and restart
./docklite status           # Show status
./docklite logs             # View logs

# Testing
./docklite test             # Run all tests (157 backend + 120+ frontend)
./docklite test-backend     # Backend only
./docklite test-frontend    # Frontend only

# Deployment
sudo ./docklite setup-user  # Create system user
sudo ./docklite setup-ssh   # Configure SSH
./docklite init-db          # Initialize database

# Maintenance
./docklite backup           # Backup system
./docklite restore <file>   # Restore from backup
./docklite clean            # Clean resources
```

## Help & Completion

```bash
# Show help
./docklite --help           # Show all commands
./docklite <command> --help # Help for specific command

# Install bash completion (smart auto-complete)
./docklite install-completion
source ~/.bashrc

# Then use Tab:
./docklite <TAB><TAB>       # Show all commands
./docklite st<TAB>          # Auto-complete
```

## Full Documentation

**[scripts/README.md](mdc:scripts/README.md)** - Complete CLI documentation with:
- All commands and options
- Usage examples
- Common library functions
- Troubleshooting
- Adding new scripts

## Structure

```
scripts/
├── docklite.sh              # Main CLI
├── lib/common.sh            # Shared functions
├── development/             # Dev commands (start, stop, rebuild, test)
├── deployment/              # Setup commands (user, ssh, db)
└── maintenance/             # Maintenance (backup, restore, clean, status)
```

**Symlink:** `./docklite` → `scripts/docklite.sh`

---

**Quick start:** [QUICKSTART.md](mdc:QUICKSTART.md)  
**Full guide:** [README.md](mdc:README.md)


### Password Recovery

Если забыли пароль:

```bash
./docklite reset-password admin     # Интерактивный ввод
./docklite reset-password admin -p newpass  # Указать пароль
```
