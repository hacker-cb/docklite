#!/bin/bash
# DockLite - List All Users
# Usage: ./list-users.sh [options]
#
# Options:
#   -h, --help      Show this help message
#   -v, --verbose   Show detailed information
#
# Examples:
#   ./list-users.sh           # List all users
#   ./list-users.sh --verbose # Detailed user info

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

print_banner "DockLite Users"

# Check Docker
check_docker

# Change to project root
cd "$(get_project_root)"

# Check if backend is running
if ! is_container_running "docklite-backend"; then
    log_warning "Backend is not running. Starting it..."
    docker_compose_cmd up -d backend
    sleep 3
fi

# Get users list
log_step "Loading users..."
echo ""

if [ "$VERBOSE" = true ]; then
    # Detailed user info
    docker_compose_cmd exec -T backend python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def list_users_detailed():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User.id, User.username, User.email, User.is_admin, User.is_active, User.system_user)
        )
        users = result.all()
        
        if not users:
            print('NO_USERS')
        else:
            # Header
            print(f'{'ID':<5} {'Username':<20} {'Email':<30} {'Role':<10} {'Status':<10} {'System User':<15}')
            print('-' * 90)
            
            for user_id, username, email, is_admin, is_active, system_user in users:
                role = 'admin' if is_admin else 'user'
                status = 'active' if is_active else 'inactive'
                email_display = email or '-'
                print(f'{user_id:<5} {username:<20} {email_display:<30} {role:<10} {status:<10} {system_user:<15}')

asyncio.run(list_users_detailed())
"
else
    # Simple list
    docker_compose_cmd exec -T backend python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def list_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.username, User.is_admin, User.is_active))
        users = result.all()
        
        if not users:
            print('NO_USERS')
        else:
            for username, is_admin, is_active in users:
                role = 'admin' if is_admin else 'user'
                status = '✓' if is_active else '✗'
                print(f'{username}:{role}:{status}')

asyncio.run(list_users())
" | while IFS=: read -r username role status; do
        if [ "$username" = "NO_USERS" ]; then
            log_warning "No users found in database!"
            log_info "Use the setup screen to create the first admin user:"
            log_info "${COLOR_CYAN}$(get_access_url)${COLOR_NC}"
            exit 1
        fi
        
        # Format output
        if [ "$role" = "admin" ]; then
            if [ "$status" = "✓" ]; then
                log_success "${COLOR_CYAN}$username${COLOR_NC} ${COLOR_YELLOW}($role)${COLOR_NC}"
            else
                log_warning "${COLOR_CYAN}$username${COLOR_NC} ${COLOR_YELLOW}($role)${COLOR_NC} ${COLOR_RED}[inactive]${COLOR_NC}"
            fi
        else
            if [ "$status" = "✓" ]; then
                log_info "${COLOR_CYAN}$username${COLOR_NC} ($role)"
            else
                log_warning "${COLOR_CYAN}$username${COLOR_NC} ($role) ${COLOR_RED}[inactive]${COLOR_NC}"
            fi
        fi
    done
fi

echo ""
log_info "Total users: ${COLOR_CYAN}$(docker_compose_cmd exec -T backend python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select, func

async def count_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count(User.id)))
        count = result.scalar()
        print(count)

asyncio.run(count_users())
" 2>/dev/null)${COLOR_NC}"

echo ""

if [ "$VERBOSE" = false ]; then
    log_info "Use ${COLOR_CYAN}--verbose${COLOR_NC} for detailed information"
fi

echo ""

