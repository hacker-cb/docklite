#!/bin/bash
# DockLite - Initialize Database
# Usage: ./init-database.sh [options]
#
# Options:
#   -h, --help       Show this help message
#   --reset          Reset database (WARNING: deletes all data!)
#
# Examples:
#   ./init-database.sh         # Run migrations
#   ./init-database.sh --reset # Reset and initialize

set -e

# Get script directory and source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$(dirname "$SCRIPT_DIR")/lib/common.sh"

# Show help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help "$0"
    exit 0
fi

print_banner "Database Initialization"

# Change to project root
cd "$(get_project_root)"

# Check if reset requested
if [ "$1" = "--reset" ]; then
    log_warning "This will DELETE all database data!"
    if ! confirm "Continue with database reset?"; then
        log_info "Cancelled"
        exit 0
    fi
    
    log_step "Removing database..."
    docker_compose_cmd down -v
    rm -f backend-data/docklite.db 2>/dev/null || true
    log_success "Database removed"
fi

# Ensure backend is running
log_step "Starting backend container..."
docker_compose_cmd up -d backend

# Wait for container
sleep 2

# Run migrations
log_step "Running database migrations..."
docker_compose_cmd exec -T backend alembic upgrade head

log_success "Database initialized!"
echo ""
log_info "Backend is ready at: ${COLOR_CYAN}$(get_access_url "/api")${COLOR_NC}"
log_info "API Docs at:         ${COLOR_CYAN}$(get_access_url "/docs")${COLOR_NC}"
echo ""

if [ "$1" = "--reset" ]; then
    log_info "Database has been reset. You'll need to create an admin user via the setup screen."
fi

