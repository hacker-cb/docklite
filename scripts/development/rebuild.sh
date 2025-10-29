#!/bin/bash
# DockLite - Rebuild and Restart
# Usage: ./rebuild.sh [options]
#
# Options:
#   -h, --help          Show this help message
#   --no-cache          Build without using cache
#   -f, --follow        Follow logs after rebuild
#
# Examples:
#   ./rebuild.sh              # Rebuild services
#   ./rebuild.sh --no-cache   # Force full rebuild

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
CACHE_FLAG=""
FOLLOW_LOGS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            CACHE_FLAG="--no-cache"
            shift
            ;;
        -f|--follow)
            FOLLOW_LOGS=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

print_banner "Rebuilding DockLite"

# Check prerequisites
check_docker
check_docker_compose

# Change to project root
cd "$(get_project_root)"

# Stop services
log_step "Stopping current services..."
docker_compose_cmd down

# Rebuild
log_step "Rebuilding images..."
docker_compose_cmd build $CACHE_FLAG

# Start
log_step "Starting services..."
docker_compose_cmd up -d

# Wait
log_step "Waiting for services..."
sleep 3

log_success "Rebuild complete!"
echo ""
print_banner "DockLite is Running"
log_info "Frontend:  ${COLOR_CYAN}$(get_access_url)${COLOR_NC}"
log_info "Backend:   ${COLOR_CYAN}$(get_access_url "/api")${COLOR_NC}"
log_info "API Docs:  ${COLOR_CYAN}$(get_access_url "/docs")${COLOR_NC}"
log_info "Dashboard: ${COLOR_CYAN}$(get_access_url "" "8888")${COLOR_NC}"
echo ""

# Follow logs if requested
if [ "$FOLLOW_LOGS" = true ]; then
    docker_compose_cmd logs -f
fi

