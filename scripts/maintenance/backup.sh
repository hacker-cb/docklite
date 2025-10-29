#!/bin/bash
# DockLite - Backup Database and Configuration
# Usage: ./backup.sh [options]
#
# Options:
#   -h, --help           Show this help message
#   -o, --output DIR     Output directory (default: ./backups)
#
# Examples:
#   ./backup.sh                    # Backup to ./backups
#   ./backup.sh -o /path/to/dir    # Custom output directory

set -e

# Get script directory and source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$(dirname "$SCRIPT_DIR")/lib/common.sh"

# Show help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help "$0"
    exit 0
fi

# Parse options
BACKUP_DIR="$(get_project_root)/backups"
if [ "$1" = "-o" ] || [ "$1" = "--output" ]; then
    BACKUP_DIR="$2"
fi

print_banner "DockLite Backup"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="docklite_backup_${TIMESTAMP}"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

log_step "Creating backup: $BACKUP_NAME"

# Create temporary directory for backup
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Backup database
log_info "Backing up database..."
cd "$(get_project_root)"
if [ -f "backend-data/docklite.db" ]; then
    cp backend-data/docklite.db "$TEMP_DIR/docklite.db"
    log_success "Database backed up"
else
    log_warning "Database file not found"
fi

# Backup configuration
log_info "Backing up configuration..."
if [ -f ".env" ]; then
    cp .env "$TEMP_DIR/.env"
fi
if [ -f "docker-compose.yml" ]; then
    cp docker-compose.yml "$TEMP_DIR/docker-compose.yml"
fi
log_success "Configuration backed up"

# Backup SSH keys (if exist)
log_info "Backing up SSH configuration..."
if [ -d "/home/docklite/.ssh" ]; then
    mkdir -p "$TEMP_DIR/ssh"
    sudo cp /home/docklite/.ssh/authorized_keys "$TEMP_DIR/ssh/" 2>/dev/null || true
fi

# Create metadata file
cat > "$TEMP_DIR/backup_info.txt" << EOF
DockLite Backup
================
Date: $(date)
Hostname: $(hostname)
Version: $(get_docklite_version)
User: $(whoami)

Contents:
- Database (SQLite)
- Configuration (.env, docker-compose.yml)
- SSH keys
EOF

# Create tar archive
log_step "Creating archive..."
cd "$TEMP_DIR"
tar -czf "${BACKUP_PATH}.tar.gz" ./*

BACKUP_SIZE=$(du -h "${BACKUP_PATH}.tar.gz" | cut -f1)

log_success "Backup created successfully!"
echo ""
print_banner "Backup Complete"
log_info "File:     ${COLOR_CYAN}${BACKUP_PATH}.tar.gz${COLOR_NC}"
log_info "Size:     ${COLOR_CYAN}${BACKUP_SIZE}${COLOR_NC}"
log_info "Location: ${COLOR_CYAN}${BACKUP_DIR}${COLOR_NC}"
echo ""
log_info "To restore: ${COLOR_CYAN}./scripts/docklite.sh restore ${BACKUP_PATH}.tar.gz${COLOR_NC}"

