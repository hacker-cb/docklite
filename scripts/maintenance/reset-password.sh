#!/bin/bash
# DockLite - Reset User Password
# Usage: ./reset-password.sh [username] [options]
#
# Options:
#   -h, --help      Show this help message
#   -p, --password  New password (interactive if not provided)
#
# Examples:
#   ./reset-password.sh admin              # Reset admin password (interactive)
#   ./reset-password.sh pavel              # Reset pavel's password
#   ./reset-password.sh admin -p newpass   # Set specific password

set -e

# Get script directory and source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$(dirname "$SCRIPT_DIR")/lib/common.sh"

# Show help
if [ "$1" = "-h" ] || [ "$1" = "--help" ] || [ -z "$1" ]; then
    show_help "$0"
    exit 0
fi

USERNAME="$1"
shift

NEW_PASSWORD=""

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--password)
            NEW_PASSWORD="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

print_banner "Reset User Password"

log_info "Username: ${COLOR_CYAN}$USERNAME${COLOR_NC}"
echo ""

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

# If password not provided, ask interactively
if [ -z "$NEW_PASSWORD" ]; then
    log_step "Enter new password for user '$USERNAME':"
    read -s -p "Password: " NEW_PASSWORD
    echo ""
    read -s -p "Confirm password: " NEW_PASSWORD_CONFIRM
    echo ""
    
    if [ "$NEW_PASSWORD" != "$NEW_PASSWORD_CONFIRM" ]; then
        log_error "Passwords don't match!"
        exit 1
    fi
    
    if [ ${#NEW_PASSWORD} -lt 6 ]; then
        log_error "Password must be at least 6 characters!"
        exit 1
    fi
fi

# Create Python script to reset password
log_step "Resetting password..."

RESET_SCRIPT=$(cat << 'PYEOF'
import asyncio
import sys
sys.path.insert(0, '/app')

# Import only what we need to avoid circular imports
from app.core.database import AsyncSessionLocal
from passlib.context import CryptContext
from sqlalchemy import select, update, text

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def reset_password(username: str, new_password: str):
    async with AsyncSessionLocal() as db:
        # Find user using raw SQL to avoid relationship issues
        result = await db.execute(
            text("SELECT id, username, email, is_admin, is_active FROM users WHERE username = :username"),
            {"username": username}
        )
        user_row = result.fetchone()
        
        if not user_row:
            print(f"ERROR: User '{username}' not found")
            return False
        
        # Hash new password
        password_hash = pwd_context.hash(new_password)
        
        # Update password
        await db.execute(
            text("UPDATE users SET password_hash = :hash WHERE username = :username"),
            {"hash": password_hash, "username": username}
        )
        await db.commit()
        
        print(f"SUCCESS: Password reset for user '{username}'")
        print(f"User ID: {user_row[0]}")
        print(f"Email: {user_row[2] or 'N/A'}")
        print(f"Admin: {'Yes' if user_row[3] else 'No'}")
        print(f"Active: {'Yes' if user_row[4] else 'No'}")
        return True

if __name__ == "__main__":
    username = sys.argv[1]
    password = sys.argv[2]
    result = asyncio.run(reset_password(username, password))
    sys.exit(0 if result else 1)
PYEOF
)

# Execute password reset
if docker_compose_cmd exec -T backend python3 -c "$RESET_SCRIPT" "$USERNAME" "$NEW_PASSWORD" 2>&1 | tee /tmp/reset_output.txt | grep -q "SUCCESS"; then
    echo ""
    log_success "Password reset successfully!"
    echo ""
    
    # Show user info
    grep -A4 "SUCCESS:" /tmp/reset_output.txt | tail -4
    
    echo ""
    log_info "You can now login with:"
    log_info "  Username: ${COLOR_CYAN}$USERNAME${COLOR_NC}"
    log_info "  Password: ${COLOR_CYAN}[your new password]${COLOR_NC}"
    echo ""
    log_info "Frontend: ${COLOR_CYAN}http://localhost:5173${COLOR_NC}"
    
else
    echo ""
    log_error "Failed to reset password"
    cat /tmp/reset_output.txt
    exit 1
fi

# Cleanup
rm -f /tmp/reset_output.txt

