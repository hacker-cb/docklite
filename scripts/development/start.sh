#!/bin/bash
# DockLite - Start Development Environment
# Usage: ./start.sh [options]
#
# Options:
#   -h, --help      Show this help message
#   -b, --build     Rebuild images before starting
#   -d, --detach    Run in detached mode (default)
#   -f, --follow    Follow logs after starting
#
# Examples:
#   ./start.sh              # Start services
#   ./start.sh --build      # Rebuild and start
#   ./start.sh --follow     # Start and show logs

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
BUILD_FLAG=""
FOLLOW_LOGS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--build)
            BUILD_FLAG="--build"
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

print_banner "Starting DockLite Development Environment"

# Check prerequisites
log_step "Checking prerequisites..."
check_docker
check_docker_compose
log_success "Docker is ready"

# Change to project root
cd "$(get_project_root)"

# Create projects directory if needed
log_step "Creating projects directory..."
mkdir -p "$HOME/docklite-projects"
log_success "Projects directory ready"

# Start services
log_step "Starting services..."
docker_compose_cmd up -d $BUILD_FLAG

# Wait for services
log_step "Waiting for services to start..."
sleep 3

# Check if containers are running
if is_container_running "docklite-backend" && is_container_running "docklite-frontend"; then
    log_success "All services started successfully!"
else
    log_warning "Some services may not have started correctly"
fi

echo ""
print_banner "DockLite is Running"
log_info "Frontend:  ${COLOR_CYAN}$(get_access_url)${COLOR_NC}"
log_info "Backend:   ${COLOR_CYAN}$(get_access_url "/api")${COLOR_NC}"
log_info "API Docs:  ${COLOR_CYAN}$(get_access_url "/docs")${COLOR_NC}"
log_info "Traefik: ${COLOR_CYAN}$(get_access_url "/traefik")${COLOR_NC} ${COLOR_YELLOW}(admin only)${COLOR_NC}"
echo ""
log_info "View logs: ${COLOR_CYAN}./scripts/docklite.sh logs${COLOR_NC}"
log_info "Stop:      ${COLOR_CYAN}./scripts/docklite.sh stop${COLOR_NC}"
echo ""

# Follow logs if requested
if [ "$FOLLOW_LOGS" = true ]; then
    docker_compose_cmd logs -f
fi

