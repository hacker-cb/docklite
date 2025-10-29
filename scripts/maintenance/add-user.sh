#!/bin/bash
# DockLite - Add New User
# Usage: ./add-user.sh <username> [options]
#
# Options:
#   -h, --help       Show this help message
#   -p, --password   Password (interactive if not provided)
#   -a, --admin      Create as admin user
#   -e, --email      Email address (optional)
#   -s, --system     System user for deployment (default: docklite)
#
# Examples:
#   ./add-user.sh cursor                     # Create user 'cursor' (interactive)
#   ./add-user.sh cursor -p Pass123 --admin  # Create admin with password
#   ./add-user.sh john -e john@example.com   # Create user with email

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

PASSWORD=""
IS_ADMIN=false
EMAIL=""
SYSTEM_USER="docklite"

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--password)
            PASSWORD="$2"
            shift 2
            ;;
        -a|--admin)
            IS_ADMIN=true
            shift
            ;;
        -e|--email)
            EMAIL="$2"
            shift 2
            ;;
        -s|--system)
            SYSTEM_USER="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

print_banner "Add New User"

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

# Check if user already exists
log_step "Checking existing users..."
USERS_LIST=$(docker_compose_cmd exec -T backend python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def check_user(username: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.username).where(User.username == username))
        user = result.scalar_one_or_none()
        if user:
            print('EXISTS')
        else:
            print('OK')

asyncio.run(check_user('$USERNAME'))
" 2>/dev/null)

if [ "$USERS_LIST" = "EXISTS" ]; then
    log_error "User '${USERNAME}' already exists!"
    log_info "Use ${COLOR_CYAN}./docklite reset-password $USERNAME${COLOR_NC} to change password"
    exit 1
fi

echo ""
log_info "Username: ${COLOR_CYAN}$USERNAME${COLOR_NC}"
if [ "$IS_ADMIN" = true ]; then
    log_info "Role: ${COLOR_YELLOW}admin${COLOR_NC}"
else
    log_info "Role: user"
fi
if [ -n "$EMAIL" ]; then
    log_info "Email: $EMAIL"
fi
log_info "System user: $SYSTEM_USER"
echo ""

# Validate username
if [ ${#USERNAME} -lt 3 ]; then
    log_error "Username must be at least 3 characters!"
    exit 1
fi

# If password not provided, ask interactively
if [ -z "$PASSWORD" ]; then
    log_step "Enter password for new user '$USERNAME':"
    read -s -p "Password: " PASSWORD
    echo ""
    read -s -p "Confirm password: " PASSWORD_CONFIRM
    echo ""
    
    if [ "$PASSWORD" != "$PASSWORD_CONFIRM" ]; then
        log_error "Passwords don't match!"
        exit 1
    fi
    
    if [ ${#PASSWORD} -lt 6 ]; then
        log_error "Password must be at least 6 characters!"
        exit 1
    fi
fi

# Validate password length
if [ ${#PASSWORD} -lt 6 ]; then
    log_error "Password must be at least 6 characters!"
    exit 1
fi

# Create Python script to add user
log_step "Creating user..."

CREATE_SCRIPT=$(cat << 'PYEOF'
import asyncio
import sys
sys.path.insert(0, '/app')

from app.core.database import AsyncSessionLocal
from passlib.context import CryptContext
from sqlalchemy import text

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(username: str, password: str, is_admin: bool, email: str, system_user: str):
    async with AsyncSessionLocal() as db:
        # Check if user exists (double-check)
        result = await db.execute(
            text("SELECT id FROM users WHERE username = :username"),
            {"username": username}
        )
        if result.fetchone():
            print(f"ERROR: User '{username}' already exists")
            return False
        
        # Hash password
        password_hash = pwd_context.hash(password)
        
        # Insert new user
        email_value = email if email else None
        await db.execute(
            text("""
                INSERT INTO users (username, password_hash, email, is_admin, is_active, system_user)
                VALUES (:username, :password_hash, :email, :is_admin, 1, :system_user)
            """),
            {
                "username": username,
                "password_hash": password_hash,
                "email": email_value,
                "is_admin": 1 if is_admin else 0,
                "system_user": system_user
            }
        )
        await db.commit()
        
        # Get created user
        result = await db.execute(
            text("SELECT id, username, email, is_admin, system_user FROM users WHERE username = :username"),
            {"username": username}
        )
        user_row = result.fetchone()
        
        print(f"SUCCESS: User created")
        print(f"User ID: {user_row[0]}")
        print(f"Username: {user_row[1]}")
        print(f"Email: {user_row[2] or 'N/A'}")
        print(f"Role: {'admin' if user_row[3] else 'user'}")
        print(f"System User: {user_row[4]}")
        return True

if __name__ == "__main__":
    username = sys.argv[1]
    password = sys.argv[2]
    is_admin = sys.argv[3] == "true"
    email = sys.argv[4] if sys.argv[4] != "NONE" else ""
    system_user = sys.argv[5]
    result = asyncio.run(create_user(username, password, is_admin, email, system_user))
    sys.exit(0 if result else 1)
PYEOF
)

# Execute user creation
IS_ADMIN_STR="false"
if [ "$IS_ADMIN" = true ]; then
    IS_ADMIN_STR="true"
fi

EMAIL_ARG="${EMAIL:-NONE}"

if docker_compose_cmd exec -T backend python3 -c "$CREATE_SCRIPT" "$USERNAME" "$PASSWORD" "$IS_ADMIN_STR" "$EMAIL_ARG" "$SYSTEM_USER" 2>&1 | tee /tmp/adduser_output.txt | grep -q "SUCCESS"; then
    echo ""
    log_success "User created successfully!"
    echo ""
    
    # Show user info
    grep -A5 "SUCCESS:" /tmp/adduser_output.txt | tail -5
    
    echo ""
    log_info "Login credentials:"
    log_info "  Username: ${COLOR_CYAN}$USERNAME${COLOR_NC}"
    log_info "  Password: ${COLOR_CYAN}[your password]${COLOR_NC}"
    echo ""
    log_info "Frontend: ${COLOR_CYAN}$(get_access_url)${COLOR_NC}"
    
else
    echo ""
    log_error "Failed to create user"
    cat /tmp/adduser_output.txt
    exit 1
fi

# Cleanup
rm -f /tmp/adduser_output.txt


