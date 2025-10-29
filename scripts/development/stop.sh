#!/bin/bash
# DockLite - Stop Development Environment
# Usage: ./stop.sh [options]
#
# Options:
#   -h, --help      Show this help message
#   -v, --volumes   Remove volumes as well
#
# Examples:
#   ./stop.sh           # Stop services
#   ./stop.sh --volumes # Stop and remove volumes

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
REMOVE_VOLUMES=""
if [ "$1" = "-v" ] || [ "$1" = "--volumes" ]; then
    REMOVE_VOLUMES="-v"
    log_warning "This will remove all volumes (including database)!"
    if ! confirm "Continue?"; then
        log_info "Cancelled"
        exit 0
    fi
fi

print_banner "Stopping DockLite"

# Change to project root
cd "$(get_project_root)"

log_step "Stopping services..."
docker_compose_cmd down $REMOVE_VOLUMES

log_success "DockLite stopped"

