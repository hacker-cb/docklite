# DockLite Scripts

Production-grade scripts for managing DockLite system.

## Quick Start

```bash
# First time setup (creates venv, installs dependencies)
./docklite dev setup-dev

# Daily commands (root level)
./docklite start          # Start system
./docklite stop           # Stop system
./docklite status         # Check status
./docklite logs           # View logs
./docklite test           # Run tests

# Show all commands
./docklite --help         # Root commands + groups
./docklite dev --help     # Development commands
./docklite user --help    # User management
```

**Note:** CLI automatically uses `.venv/` virtual environment - no need to activate manually!

## Command Structure

DockLite uses **hybrid command structure** for optimal usability:
- **6 Root Commands** - Daily-use commands for quick access
- **4 Command Groups** - Specialized commands organized by function

```
./docklite <command>              # Root commands (start, stop, logs, etc.)
./docklite <group> <subcommand>   # Grouped commands (dev, deploy, user, maint)
```

## Structure

```
scripts/
├── docklite.sh           # Main CLI wrapper
├── lib/
│   └── common.sh         # Shared functions (logging, colors, helpers)
├── development/
│   ├── start.sh         # Start DockLite services
│   ├── stop.sh          # Stop services
│   ├── rebuild.sh       # Rebuild and restart
│   ├── test-all.sh      # Run all tests
│   ├── test-backend.sh  # Backend tests only
│   └── test-frontend.sh # Frontend tests only
├── deployment/
│   ├── setup-system-user.sh  # Create system user (docklite)
│   ├── configure-ssh.sh      # Setup SSH for localhost
│   └── init-database.sh      # Initialize/reset database
└── maintenance/
    ├── backup.sh        # Backup database and config
    ├── restore.sh       # Restore from backup
    ├── clean.sh         # Clean unused Docker resources
    └── status.sh        # Show system status
```

## Commands

### Root Level Commands (6)

Essential daily-use commands available at root level:

#### `start` - Start Services
```bash
./docklite start                # Normal start
./docklite start --build        # Rebuild images first
./docklite start --follow       # Start and follow logs
```

#### `stop` - Stop Services
```bash
./docklite stop                 # Stop services
./docklite stop --volumes       # Stop and remove volumes (WARNING: deletes data!)
```

#### `restart` - Restart Services
```bash
./docklite restart              # Stop then start
./docklite restart --build      # Rebuild before restart
```

#### `logs` - Show Logs
```bash
./docklite logs                 # Follow all logs
./docklite logs backend         # Backend only
./docklite logs frontend        # Frontend only
./docklite logs traefik         # Traefik only
```

#### `status` - System Status
```bash
./docklite status               # Basic status
./docklite status --verbose     # Detailed info (disk, db, projects)
```

Shows:
- Container status (running/stopped)
- Access URLs
- Version info
- Disk usage (verbose)
- Database info (verbose)
- Projects count (verbose)

#### `test` - Run All Tests
```bash
./docklite test                 # All tests (backend + frontend)
./docklite test --verbose       # Verbose output
./docklite test --quiet         # Minimal output
```

---

### Development Group (`dev`) - 5 Commands

Development and testing commands:

#### `dev setup-dev` - First-Time Setup
```bash
./docklite dev setup-dev        # Create venv, install deps, setup .env
```

What it does:
- Creates `.venv/` virtual environment
- Installs CLI dependencies (typer, rich, python-dotenv, PyYAML)
- Creates `.env` from `.env.example`
- Checks Docker
- Makes CLI executable

#### `dev rebuild` - Rebuild Images
```bash
./docklite dev rebuild              # Rebuild with cache
./docklite dev rebuild --no-cache   # Full rebuild
./docklite dev rebuild --follow     # Rebuild and show logs
```

#### `dev test-backend` - Backend Tests
```bash
./docklite dev test-backend             # All backend tests
./docklite dev test-backend -v          # Verbose
./docklite dev test-backend -k auth     # Auth tests only
./docklite dev test-backend --cov       # With coverage
```

#### `dev test-frontend` - Frontend Tests
```bash
./docklite dev test-frontend            # All frontend tests
./docklite dev test-frontend --watch    # Watch mode
./docklite dev test-frontend --ui       # Interactive UI
./docklite dev test-frontend --coverage # Coverage report
```

#### `dev test-e2e` - E2E Tests (Playwright)
```bash
./docklite dev test-e2e             # Run all E2E tests
./docklite dev test-e2e --ui        # Interactive UI mode
./docklite dev test-e2e --debug     # Debug mode (step through)
./docklite dev test-e2e --report    # Show test report
./docklite dev test-e2e --headed    # Show browser while testing
```

**Prerequisites:**
- Playwright: `cd frontend && npm install @playwright/test && npx playwright install chromium`
- Test users: `cursor` (admin) and `testuser` (user)

---

### Deployment Group (`deploy`) - 3 Commands

Production deployment commands (Linux only):

#### `deploy setup-user` - Create System User
```bash
sudo ./docklite deploy setup-user      # Create 'docklite' user

# Custom user
DEPLOY_USER=myuser sudo ./docklite deploy setup-user
```

Creates Linux user for project deployment:
- Home directory `/home/{user}`
- Projects directory `/home/{user}/projects`
- SSH configuration
- Docker group membership

#### `deploy setup-ssh` - Configure SSH
```bash
sudo ./docklite deploy setup-ssh       # Setup SSH for localhost
```

Configures:
- SSH keys for current user
- Adds key to docklite user's authorized_keys
- Unlocks docklite account
- Tests SSH connection

#### `deploy init-db` - Initialize Database
```bash
./docklite deploy init-db              # Run migrations
./docklite deploy init-db --reset      # Reset database (WARNING: deletes all data!)
```

---

### User Management Group (`user`) - 3 Commands

User administration commands:

#### `user add` - Add New User
```bash
./docklite user add admin -p "Pass123" --admin    # Add admin user
./docklite user add username                      # Add user (interactive password)
./docklite user add john -p "Pass" --email j@ex.com  # With email
```

Options:
- `-p, --password` - Password (prompted if not provided)
- `-a, --admin` - Create as admin user
- `-e, --email` - Email address
- `-s, --system-user` - Linux system user for projects (default: docklite)

**Security:** Password must be at least 8 characters

#### `user list` - List Users
```bash
./docklite user list                   # Simple list
./docklite user list --verbose         # Detailed table with IDs, emails, etc.
```

Shows:
- Username and role (admin/user)
- Status (active/inactive)
- System user assignment
- Email (verbose mode)
- User ID (verbose mode)

#### `user reset-password` - Reset Password
```bash
./docklite user reset-password admin            # Interactive password entry
./docklite user reset-password john             # Reset any user
./docklite user reset-password admin -p newpass # Set specific password
```

**Use case:** Forgot password, locked out of admin account

**Security:** Password must be at least 6 characters

---

### Maintenance Group (`maint`) - 3 Commands

System maintenance commands:

#### `maint backup` - Backup System
```bash
./docklite maint backup               # Backup to ./backups
./docklite maint backup -o /path/dir  # Custom output directory
```

Backs up:
- SQLite database
- Configuration files (.env, docker-compose.yml)
- SSH keys
- Creates timestamped tar.gz archive

#### `maint restore` - Restore from Backup
```bash
./docklite maint restore backups/docklite_backup_20250129.tar.gz
./docklite maint restore backup.tar.gz --no-confirm
```

**WARNING:** Replaces current data! Creates safety backup before restore.

#### `maint clean` - Clean Resources
```bash
./docklite maint clean                # Interactive menu
./docklite maint clean --all          # Clean everything
./docklite maint clean --images       # Unused images only
./docklite maint clean --volumes      # Unused volumes only
./docklite maint clean --logs         # Log files only
```

---

## Common Library (`lib/common.sh`)

Shared functions available to all scripts:

### Logging
```bash
log_info "Information message"
log_success "Success message"  
log_warning "Warning message"
log_error "Error message"
log_step "Step description"
```

### Checks
```bash
check_root            # Ensure running as root
check_not_root        # Ensure NOT running as root
check_docker          # Check Docker installed and running
check_docker_compose  # Check docker-compose available
```

### Docker Helpers
```bash
docker_compose_cmd up -d        # Works with both docker-compose and docker compose
is_container_running "name"     # Check if container is running
```

### User Helpers
```bash
get_actual_user       # Get actual user (even when using sudo)
get_actual_home       # Get actual user's home directory
user_exists "username"  # Check if user exists
```

### File Helpers
```bash
backup_file "/path/to/file"     # Create timestamped backup
```

### Utilities
```bash
confirm "Question?"             # Yes/no prompt
print_banner "Title"            # Pretty banner
get_docklite_version           # Get version
get_project_root               # Get project root path
```

---

## Examples

### Daily Development Workflow
```bash
# Morning - start system
./docklite start

# Check if everything is running
./docklite status

# Make changes, run tests
./docklite test

# View logs if needed
./docklite logs

# Evening - stop system
./docklite stop
```

### First-Time Setup
```bash
# Setup development environment
./docklite dev setup-dev

# Start system
./docklite start

# Create admin user
./docklite user add admin -p "YourPassword" --admin

# Check status
./docklite status -v
```

### Deployment Setup (Production)
```bash
# 1. Create system user
sudo ./docklite deploy setup-user

# 2. Setup SSH
sudo ./docklite deploy setup-ssh

# 3. Initialize database
./docklite deploy init-db

# 4. Start system
./docklite start

# 5. Create admin
./docklite user add admin -p "SecurePass" --admin
```

### Backup & Restore
```bash
# Create backup before major changes
./docklite maint backup

# If something goes wrong, restore
./docklite maint restore backups/docklite_backup_TIMESTAMP.tar.gz
```

### Maintenance
```bash
# Check system status
./docklite status --verbose

# Clean up disk space
./docklite maint clean --all

# Create regular backups
./docklite maint backup -o /backups/docklite/

# Manage users
./docklite user list --verbose
./docklite user add newuser
./docklite user reset-password username
```

---

## Environment Variables

Some scripts support environment variables:

### setup-user
```bash
DEPLOY_USER=custom ./docklite setup-user       # Custom username
PROJECTS_DIR=/custom/path ./docklite setup-user  # Custom projects dir
```

### All scripts
```bash
# Colors can be disabled
export NO_COLOR=1
```

---

## Exit Codes

All scripts follow standard exit codes:
- `0` - Success
- `1` - General error
- `2` - Misuse of command

---

## Tips

### Enable Tab Completion

DockLite includes smart bash completion! Install it:

```bash
./docklite install-completion
source ~/.bashrc
```

Then enjoy auto-completion:
```bash
./docklite <TAB><TAB>        # Show all commands
./docklite st<TAB>            # Complete start/status
./docklite logs <TAB>         # Complete backend/frontend
./docklite restore <TAB>      # Complete .tar.gz files
```

**Full docs:** [scripts/completion/README.md](mdc:completion/README.md)

### Alias for Convenience
```bash
# Add to ~/.bashrc
alias dl='./docklite'

# Then use:
dl start
dl test
dl status
```

### Regular Maintenance
```bash
# Weekly backup
./docklite backup -o /backups/weekly/

# Monthly cleanup
./docklite clean --all
```

---

## Troubleshooting

### Permission Denied
```bash
# Make sure scripts are executable
chmod +x scripts/docklite.sh scripts/**/*.sh

# Or use bash explicitly
bash ./docklite start
```

### Docker Not Running
```bash
# Start Docker service
sudo systemctl start docker

# Check status
./docklite status
```

### Database Issues
```bash
# Reset database (WARNING: deletes data!)
./docklite init-db --reset

# Or restore from backup
./docklite restore backups/your_backup.tar.gz
```

---

## Development

### Adding New Scripts

1. Create script in appropriate directory:
   ```bash
   touch scripts/development/my-script.sh
   chmod +x scripts/development/my-script.sh
   ```

2. Use template:
   ```bash
   #!/bin/bash
   # DockLite - Script Description
   # Usage: ./my-script.sh [options]
   #
   # Options:
   #   -h, --help      Show this help message
   
   set -e
   
   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   source "$(dirname "$SCRIPT_DIR")/lib/common.sh"
   
   if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
       show_help "$0"
       exit 0
   fi
   
   print_banner "My Script"
   log_step "Doing something..."
   # Your code here
   log_success "Done!"
   ```

3. Add command to `docklite.sh`:
   ```bash
   my-command)
       exec "$SCRIPT_DIR/development/my-script.sh" "$@"
       ;;
   ```

4. Update this README

---

## License

MIT - Part of DockLite project

