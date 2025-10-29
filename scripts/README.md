# DockLite Scripts

Production-grade scripts for managing DockLite system.

## Quick Start

```bash
# From project root
./docklite start          # Start system
./docklite status         # Check status
./docklite test           # Run tests
./docklite --help         # Show all commands
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

### Development

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
```

#### `rebuild` - Rebuild and Restart
```bash
./docklite rebuild              # Rebuild with cache
./docklite rebuild --no-cache   # Full rebuild
./docklite rebuild --follow     # Rebuild and show logs
```

#### `logs` - Show Logs
```bash
./docklite logs                 # Follow all logs
./docklite logs backend         # Backend only
./docklite logs frontend        # Frontend only
```

#### `test` - Run Tests
```bash
./docklite test                 # All tests
./docklite test --verbose       # Verbose output
./docklite test --quiet         # Minimal output
```

#### `test-backend` - Backend Tests
```bash
./docklite test-backend         # All backend tests
./docklite test-backend -v      # Verbose
./docklite test-backend -k auth # Auth tests only
./docklite test-backend --cov   # With coverage
```

#### `test-frontend` - Frontend Tests
```bash
./docklite test-frontend        # All frontend tests
./docklite test-frontend --watch    # Watch mode
./docklite test-frontend --ui       # Interactive UI
./docklite test-frontend --coverage # Coverage report
```

---

### Deployment

#### `setup-user` - Create System User
```bash
sudo ./docklite setup-user      # Create 'docklite' user

# Custom user
DEPLOY_USER=myuser sudo ./docklite setup-user
```

Creates Linux user for project deployment with:
- Home directory `/home/{user}`
- Projects directory `/home/{user}/projects`
- SSH configuration
- Docker group membership

#### `setup-ssh` - Configure SSH
```bash
sudo ./docklite setup-ssh       # Setup SSH for localhost
```

Configures:
- SSH keys for current user
- Adds key to docklite user's authorized_keys
- Unlocks docklite account
- Tests SSH connection

#### `init-db` - Initialize Database
```bash
./docklite init-db              # Run migrations
./docklite init-db --reset      # Reset database (WARNING: deletes all data!)
```

---

### Maintenance

#### `backup` - Backup System
```bash
./docklite backup               # Backup to ./backups
./docklite backup -o /path/dir  # Custom output directory
```

Backs up:
- SQLite database
- Configuration files (.env, docker-compose.yml)
- SSH keys
- Creates timestamped tar.gz archive

#### `restore` - Restore from Backup
```bash
./docklite restore backups/docklite_backup_20250129.tar.gz
./docklite restore backup.tar.gz --no-confirm
```

**WARNING:** This replaces current data! Creates safety backup before restore.

#### `clean` - Clean Resources
```bash
./docklite clean                # Interactive menu
./docklite clean --all          # Clean everything
./docklite clean --images       # Unused images only
./docklite clean --volumes      # Unused volumes only
./docklite clean --logs         # Log files only
```

#### `status` - System Status
```bash
./docklite status               # Basic status
./docklite status --verbose     # Detailed info
```

Shows:
- Container status (running/stopped)
- Access URLs
- Version info
- Disk usage (verbose)
- Database info (verbose)
- Projects count (verbose)

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

### Deployment Setup
```bash
# 1. Create system user
sudo ./docklite setup-user

# 2. Setup SSH
sudo ./docklite setup-ssh

# 3. Initialize database
./docklite init-db

# 4. Start system
./docklite start
```

### Backup & Restore
```bash
# Create backup before major changes
./docklite backup

# If something goes wrong, restore
./docklite restore backups/docklite_backup_TIMESTAMP.tar.gz
```

### Maintenance
```bash
# Check system status
./docklite status --verbose

# Clean up disk space
./docklite clean --all

# Create regular backups
./docklite backup -o /backups/docklite/
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

### Use Tab Completion
```bash
# Enable tab completion (add to ~/.bashrc)
complete -W "start stop restart rebuild logs test test-backend test-frontend setup-user setup-ssh init-db backup restore clean status version help" ./docklite
```

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

