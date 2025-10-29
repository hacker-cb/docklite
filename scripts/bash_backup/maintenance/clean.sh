#!/bin/bash
# DockLite - Clean Up Unused Resources
# Usage: ./clean.sh [options]
#
# Options:
#   -h, --help      Show this help message
#   --all           Clean everything (images, volumes, etc.)
#   --images        Clean unused images only
#   --volumes       Clean unused volumes only
#   --logs          Clean log files
#
# Examples:
#   ./clean.sh          # Interactive cleanup
#   ./clean.sh --all    # Clean everything

set -e

# Get script directory and source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$(dirname "$SCRIPT_DIR")/lib/common.sh"

# Show help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help "$0"
    exit 0
fi

print_banner "DockLite Cleanup"

# Parse options
CLEAN_ALL=false
CLEAN_IMAGES=false
CLEAN_VOLUMES=false
CLEAN_LOGS=false

case "$1" in
    --all)
        CLEAN_ALL=true
        ;;
    --images)
        CLEAN_IMAGES=true
        ;;
    --volumes)
        CLEAN_VOLUMES=true
        ;;
    --logs)
        CLEAN_LOGS=true
        ;;
    "")
        # Interactive mode
        echo "What would you like to clean?"
        echo "1) Unused Docker images"
        echo "2) Unused Docker volumes"
        echo "3) Log files"
        echo "4) All of the above"
        echo "5) Cancel"
        read -p "Select option [1-5]: " choice
        
        case $choice in
            1) CLEAN_IMAGES=true ;;
            2) CLEAN_VOLUMES=true ;;
            3) CLEAN_LOGS=true ;;
            4) CLEAN_ALL=true ;;
            5) log_info "Cancelled"; exit 0 ;;
            *) log_error "Invalid choice"; exit 1 ;;
        esac
        ;;
esac

if [ "$CLEAN_ALL" = true ]; then
    CLEAN_IMAGES=true
    CLEAN_VOLUMES=true
    CLEAN_LOGS=true
fi

# Clean unused images
if [ "$CLEAN_IMAGES" = true ]; then
    log_step "Cleaning unused Docker images..."
    docker image prune -f
    log_success "Unused images removed"
fi

# Clean unused volumes
if [ "$CLEAN_VOLUMES" = true ]; then
    log_warning "This will remove unused volumes!"
    if confirm "Continue?"; then
        log_step "Cleaning unused Docker volumes..."
        docker volume prune -f
        log_success "Unused volumes removed"
    fi
fi

# Clean logs
if [ "$CLEAN_LOGS" = true ]; then
    log_step "Cleaning log files..."
    cd "$(get_project_root)"
    
    # Truncate Docker logs
    docker_compose_cmd ps -q | xargs -I {} docker inspect --format='{{.LogPath}}' {} | xargs -I {} sudo truncate -s 0 {} 2>/dev/null || true
    
    log_success "Logs cleaned"
fi

# Show disk usage
log_step "Disk usage after cleanup:"
docker system df

log_success "Cleanup complete!"

