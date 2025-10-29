#!/bin/bash
# DockLite - Restore from Backup
# Usage: ./restore.sh <backup_file> [options]
#
# Options:
#   -h, --help      Show this help message
#   --no-confirm    Skip confirmation prompt
#
# Examples:
#   ./restore.sh backups/docklite_backup_20250129.tar.gz
#   ./restore.sh backup.tar.gz --no-confirm

set -e

# Get script directory and source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$(dirname "$SCRIPT_DIR")/lib/common.sh"

# Show help
if [ "$1" = "-h" ] || [ "$1" = "--help" ] || [ -z "$1" ]; then
    show_help "$0"
    exit 0
fi

BACKUP_FILE="$1"
SKIP_CONFIRM=false

if [ "$2" = "--no-confirm" ]; then
    SKIP_CONFIRM=true
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    log_error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

print_banner "DockLite Restore"

log_warning "This will REPLACE current database and configuration!"
if [ "$SKIP_CONFIRM" = false ]; then
    if ! confirm "Continue with restore?"; then
        log_info "Cancelled"
        exit 0
    fi
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Extract backup
log_step "Extracting backup..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"
log_success "Backup extracted"

# Show backup info
if [ -f "$TEMP_DIR/backup_info.txt" ]; then
    echo ""
    cat "$TEMP_DIR/backup_info.txt"
    echo ""
fi

# Stop services
log_step "Stopping services..."
cd "$(get_project_root)"
docker_compose_cmd down

# Backup current state
log_step "Backing up current state..."
SAFETY_BACKUP="$(get_project_root)/backups/pre_restore_$(date +%Y%m%d_%H%M%S).tar.gz"
mkdir -p "$(get_project_root)/backups"
tar -czf "$SAFETY_BACKUP" backend-data/ .env docker-compose.yml 2>/dev/null || true
log_success "Safety backup created: $SAFETY_BACKUP"

# Restore database
log_step "Restoring database..."
if [ -f "$TEMP_DIR/docklite.db" ]; then
    mkdir -p backend-data
    cp "$TEMP_DIR/docklite.db" backend-data/docklite.db
    log_success "Database restored"
fi

# Restore configuration
log_step "Restoring configuration..."
if [ -f "$TEMP_DIR/.env" ]; then
    cp "$TEMP_DIR/.env" .env
fi
if [ -f "$TEMP_DIR/docker-compose.yml" ]; then
    cp "$TEMP_DIR/docker-compose.yml" docker-compose.yml
fi
log_success "Configuration restored"

# Restore SSH keys
if [ -f "$TEMP_DIR/ssh/authorized_keys" ]; then
    log_step "Restoring SSH keys..."
    sudo mkdir -p /home/docklite/.ssh
    sudo cp "$TEMP_DIR/ssh/authorized_keys" /home/docklite/.ssh/
    sudo chown -R docklite:docklite /home/docklite/.ssh
    sudo chmod 600 /home/docklite/.ssh/authorized_keys
    log_success "SSH keys restored"
fi

# Restart services
log_step "Starting services..."
docker_compose_cmd up -d

sleep 3

log_success "Restore complete!"
echo ""
log_info "DockLite has been restored from backup"
log_info "Safety backup saved at: ${COLOR_CYAN}${SAFETY_BACKUP}${COLOR_NC}"

