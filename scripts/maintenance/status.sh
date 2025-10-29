#!/bin/bash
# DockLite - Show System Status
# Usage: ./status.sh [options]
#
# Options:
#   -h, --help      Show this help message
#   -v, --verbose   Show detailed information
#
# Examples:
#   ./status.sh           # Show status
#   ./status.sh --verbose # Detailed status

set -e

# Get script directory and source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$(dirname "$SCRIPT_DIR")/lib/common.sh"

# Show help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help "$0"
    exit 0
fi

VERBOSE=false
if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
    VERBOSE=true
fi

print_banner "DockLite System Status"

cd "$(get_project_root)"

# Check containers
echo ""
log_step "Container Status:"
docker_compose_cmd ps

# Check if containers are running
echo ""
if is_container_running "docklite-traefik"; then
    log_success "Traefik:  ${COLOR_GREEN}Running${COLOR_NC}"
else
    log_error "Traefik:  ${COLOR_RED}Stopped${COLOR_NC}"
fi

if is_container_running "docklite-backend"; then
    log_success "Backend:  ${COLOR_GREEN}Running${COLOR_NC}"
else
    log_error "Backend:  ${COLOR_RED}Stopped${COLOR_NC}"
fi

if is_container_running "docklite-frontend"; then
    log_success "Frontend: ${COLOR_GREEN}Running${COLOR_NC}"
else
    log_error "Frontend: ${COLOR_RED}Stopped${COLOR_NC}"
fi

# Show URLs
if is_container_running "docklite-traefik" && is_container_running "docklite-backend" && is_container_running "docklite-frontend"; then
    echo ""
    log_step "Access URLs (via Traefik):"
    log_info "Frontend:         ${COLOR_CYAN}http://localhost${COLOR_NC}"
    log_info "Backend API:      ${COLOR_CYAN}http://localhost/api${COLOR_NC}"
    log_info "API Docs:         ${COLOR_CYAN}http://localhost/docs${COLOR_NC}"
    log_info "Traefik Dashboard: ${COLOR_CYAN}http://localhost:8888${COLOR_NC}"
fi

# Show version
echo ""
log_step "Version:"
log_info "DockLite: ${COLOR_CYAN}v$(get_docklite_version)${COLOR_NC}"

# Show disk usage
if [ "$VERBOSE" = true ]; then
    echo ""
    log_step "Docker Disk Usage:"
    docker system df
    
    echo ""
    log_step "Database Info:"
    if [ -f "backend-data/docklite.db" ]; then
        DB_SIZE=$(du -h backend-data/docklite.db | cut -f1)
        log_info "Database size: ${COLOR_CYAN}${DB_SIZE}${COLOR_NC}"
        log_info "Location: ${COLOR_CYAN}backend-data/docklite.db${COLOR_NC}"
    else
        log_warning "Database not found"
    fi
    
    echo ""
    log_step "Projects Directory:"
    if [ -d "/home/docklite/projects" ]; then
        PROJECT_COUNT=$(sudo find /home/docklite/projects -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
        log_info "Projects: ${COLOR_CYAN}${PROJECT_COUNT}${COLOR_NC}"
    else
        log_warning "Projects directory not found"
    fi
fi

echo ""

