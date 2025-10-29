#!/bin/bash
# DockLite - Common Functions Library
# Shared functions for all DockLite scripts

# Colors
export COLOR_RED='\033[0;31m'
export COLOR_GREEN='\033[0;32m'
export COLOR_YELLOW='\033[1;33m'
export COLOR_BLUE='\033[0;34m'
export COLOR_CYAN='\033[0;36m'
export COLOR_NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${COLOR_BLUE}ℹ${COLOR_NC} $1"
}

log_success() {
    echo -e "${COLOR_GREEN}✅${COLOR_NC} $1"
}

log_warning() {
    echo -e "${COLOR_YELLOW}⚠️${COLOR_NC}  $1"
}

log_error() {
    echo -e "${COLOR_RED}❌${COLOR_NC} $1" >&2
}

log_step() {
    echo -e "${COLOR_CYAN}▶${COLOR_NC} $1"
}

# Utility functions
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_not_root() {
    if [ "$EUID" -eq 0 ]; then
        log_error "This script should NOT be run as root"
        exit 1
    fi
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running"
        exit 1
    fi
}

check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "docker-compose is not installed"
        exit 1
    fi
}

get_actual_user() {
    if [ -n "$SUDO_USER" ]; then
        echo "$SUDO_USER"
    else
        echo "$USER"
    fi
}

get_actual_home() {
    local user=$(get_actual_user)
    eval echo ~$user
}

# Docker helpers
docker_compose_cmd() {
    # Use sg docker if not in docker group
    if groups | grep -q docker; then
        if command -v docker-compose &> /dev/null; then
            docker-compose "$@"
        else
            docker compose "$@"
        fi
    else
        if command -v docker-compose &> /dev/null; then
            sg docker -c "docker-compose $*"
        else
            sg docker -c "docker compose $*"
        fi
    fi
}

is_container_running() {
    local container=$1
    if groups | grep -q docker; then
        docker ps --format '{{.Names}}' | grep -q "^${container}$"
    else
        sg docker -c "docker ps --format '{{.Names}}'" | grep -q "^${container}$"
    fi
}

# File helpers
backup_file() {
    local file=$1
    local backup="${file}.backup.$(date +%Y%m%d_%H%M%S)"
    
    if [ -f "$file" ]; then
        cp "$file" "$backup"
        log_success "Backup created: $backup"
    fi
}

# User helpers
user_exists() {
    id "$1" &>/dev/null
}

# Confirmation prompt
confirm() {
    local prompt="${1:-Are you sure?}"
    local default="${2:-n}"
    
    if [ "$default" = "y" ] || [ "$default" = "Y" ]; then
        prompt="$prompt [Y/n] "
        default_resp="y"
    else
        prompt="$prompt [y/N] "
        default_resp="n"
    fi
    
    read -p "$prompt" -n 1 -r
    echo
    
    if [ -z "$REPLY" ]; then
        REPLY=$default_resp
    fi
    
    [[ $REPLY =~ ^[Yy]$ ]]
}

# Parse help from script
show_help() {
    local script=$1
    if [ -f "$script" ]; then
        sed -n '/^# Usage:/,/^$/p' "$script" | sed 's/^# *//'
    fi
}

# Hostname detection with priority logic
get_hostname() {
    # Priority 1: HOSTNAME from .env file
    if [ -f "$(get_project_root)/.env" ]; then
        local env_hostname=$(grep "^HOSTNAME=" "$(get_project_root)/.env" 2>/dev/null | cut -d'=' -f2- | tr -d ' "'"'"'')
        if [ -n "$env_hostname" ]; then
            echo "$env_hostname"
            return 0
        fi
    fi
    
    # Priority 2: System hostname (if valid)
    local sys_hostname=$(hostname 2>/dev/null)
    if [ -n "$sys_hostname" ] && [ "$sys_hostname" != "localhost" ]; then
        # Check if it's not an IP address
        if ! echo "$sys_hostname" | grep -qE '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'; then
            echo "$sys_hostname"
            return 0
        fi
    fi
    
    # Priority 3: Default to localhost
    echo "localhost"
}

# Get full access URL
get_access_url() {
    local path="${1:-}"
    local port="${2:-}"
    local protocol="${3:-http}"
    
    local hostname=$(get_hostname)
    local url="${protocol}://${hostname}"
    
    # Add port if specified and not default
    if [ -n "$port" ] && [ "$port" != "80" ] && [ "$port" != "443" ]; then
        url="${url}:${port}"
    fi
    
    # Add path
    if [ -n "$path" ]; then
        # Ensure path starts with /
        if [[ ! "$path" =~ ^/ ]]; then
            path="/$path"
        fi
        url="${url}${path}"
    fi
    
    echo "$url"
}

# Version info
get_docklite_version() {
    echo "1.0.0"
}

# Project paths
get_project_root() {
    echo "/home/pavel/docklite"
}

get_scripts_dir() {
    echo "$(get_project_root)/scripts"
}

# Banner
print_banner() {
    local title="$1"
    echo "╔════════════════════════════════════════════════════════════╗"
    printf "║ %-58s ║\n" "$title"
    echo "╚════════════════════════════════════════════════════════════╝"
}

# Progress indicator
spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

