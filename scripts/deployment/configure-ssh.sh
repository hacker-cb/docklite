#!/bin/bash
# DockLite - Configure SSH for Localhost Deployment
# Usage: ./configure-ssh.sh [options]
#
# Options:
#   -h, --help      Show this help message
#   -u, --user      Deploy user (default: docklite)
#
# Examples:
#   sudo ./configure-ssh.sh           # Configure for 'docklite'
#   sudo ./configure-ssh.sh -u myuser # Configure for 'myuser'

set -e

# Get script directory and source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$(dirname "$SCRIPT_DIR")/lib/common.sh"

# Show help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help "$0"
    exit 0
fi

# Check root
check_root

DEPLOY_USER="${DEPLOY_USER:-docklite}"
DEPLOY_HOME="/home/$DEPLOY_USER"

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--user)
            DEPLOY_USER="$2"
            DEPLOY_HOME="/home/$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Determine the actual user (who ran sudo)
ACTUAL_USER=$(get_actual_user)
ACTUAL_HOME=$(get_actual_home)
SSH_KEY="$ACTUAL_HOME/.ssh/id_ed25519"

print_banner "DockLite SSH Configuration for Localhost"

log_info "Actual user: ${COLOR_CYAN}$ACTUAL_USER${COLOR_NC}"
log_info "Deploy user: ${COLOR_CYAN}$DEPLOY_USER${COLOR_NC}"
log_info "SSH key: ${COLOR_CYAN}$SSH_KEY${COLOR_NC}"
echo ""

# Step 1: Ensure deploy user exists and is unlocked
log_step "1️⃣  Checking deploy user..."
if ! user_exists "$DEPLOY_USER"; then
    log_error "User '$DEPLOY_USER' doesn't exist. Run: ./docklite setup-user"
    exit 1
fi
log_success "User '$DEPLOY_USER' exists"

# Check if account is locked
if passwd -S "$DEPLOY_USER" | grep -q " L "; then
    log_step "Unlocking account..."
    usermod -p '*' "$DEPLOY_USER"
    log_success "Account unlocked"
fi

# Step 2: Fix ~/.ssh permissions for actual user
log_step "2️⃣  Fixing ~/.ssh permissions for $ACTUAL_USER..."
if [ -d "$ACTUAL_HOME/.ssh" ]; then
    chown -R $ACTUAL_USER:$ACTUAL_USER "$ACTUAL_HOME/.ssh"
    chmod 700 "$ACTUAL_HOME/.ssh"
    log_success "Permissions fixed"
else
    mkdir -p "$ACTUAL_HOME/.ssh"
    chown $ACTUAL_USER:$ACTUAL_USER "$ACTUAL_HOME/.ssh"
    chmod 700 "$ACTUAL_HOME/.ssh"
    log_success "Created ~/.ssh"
fi

# Step 3: Generate SSH key if doesn't exist
log_step "3️⃣  Checking SSH key..."
if [ -f "$SSH_KEY" ]; then
    log_warning "SSH key already exists: $SSH_KEY"
    log_info "Using existing key"
else
    log_step "Generating new SSH key for $ACTUAL_USER..."
    sudo -u $ACTUAL_USER ssh-keygen -t ed25519 -C "docklite@localhost" -f "$SSH_KEY" -N ""
    log_success "SSH key created: $SSH_KEY"
fi

# Ensure key has correct permissions
chmod 600 "$SSH_KEY" 2>/dev/null || true
chown $ACTUAL_USER:$ACTUAL_USER "$SSH_KEY" 2>/dev/null || true

# Step 4: Setup .ssh for deploy user
log_step "4️⃣  Setting up .ssh for $DEPLOY_USER..."
mkdir -p "$DEPLOY_HOME/.ssh"
touch "$DEPLOY_HOME/.ssh/authorized_keys"
chmod 700 "$DEPLOY_HOME/.ssh"
chmod 600 "$DEPLOY_HOME/.ssh/authorized_keys"
chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_HOME/.ssh"
log_success "Directory configured"

# Step 5: Add public key to authorized_keys
log_step "5️⃣  Adding SSH key to authorized_keys..."
PUBKEY=$(cat "$SSH_KEY.pub")

# Check if key already exists
if grep -qF "$PUBKEY" "$DEPLOY_HOME/.ssh/authorized_keys" 2>/dev/null; then
    log_warning "Key already in authorized_keys"
else
    echo "$PUBKEY" >> "$DEPLOY_HOME/.ssh/authorized_keys"
    log_success "Key added"
fi

# Fix permissions again
chmod 600 "$DEPLOY_HOME/.ssh/authorized_keys"
chown $DEPLOY_USER:$DEPLOY_USER "$DEPLOY_HOME/.ssh/authorized_keys"

# Step 6: Create projects directory
log_step "6️⃣  Creating projects directory..."
mkdir -p "$DEPLOY_HOME/projects"
chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_HOME/projects"
chmod 755 "$DEPLOY_HOME/projects"
log_success "Projects directory ready"

# Step 7: Test SSH connection
log_step "7️⃣  Testing SSH connection..."
SSH_TEST_OUTPUT=$(sudo -u $ACTUAL_USER ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null $DEPLOY_USER@localhost 'echo "SSH_OK"' 2>&1)

if echo "$SSH_TEST_OUTPUT" | grep -q "SSH_OK"; then
    log_success "SSH connection works!"
    SSH_OK=true
else
    log_error "SSH connection failed"
    log_info "Output: $SSH_TEST_OUTPUT"
    SSH_OK=false
fi

# Step 8: Test docker access
if [ "$SSH_OK" = true ]; then
    log_step "8️⃣  Testing docker-compose access..."
    if sudo -u $ACTUAL_USER ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $DEPLOY_USER@localhost 'which docker-compose || which docker' &>/dev/null; then
        log_success "docker-compose is accessible"
    else
        log_warning "docker-compose not found"
        log_info "User was added to docker group, but needs re-login"
    fi
fi

# Summary
echo ""
print_banner "Setup Complete!"
echo ""

if [ "$SSH_OK" = true ]; then
    log_success "All checks passed!"
    echo ""
    log_info "You can now:"
    log_info "1. Start DockLite: ${COLOR_CYAN}./docklite start${COLOR_NC}"
    log_info "2. Test deployment: ${COLOR_CYAN}ssh $DEPLOY_USER@localhost${COLOR_NC}"
    log_info "3. Check logs: ${COLOR_CYAN}./docklite logs${COLOR_NC}"
else
    log_error "SSH setup incomplete"
    echo ""
    log_info "Try these steps:"
    log_info "1. Check SSH server: ${COLOR_CYAN}sudo systemctl status sshd${COLOR_NC}"
    log_info "2. Test manually: ${COLOR_CYAN}ssh -v $DEPLOY_USER@localhost${COLOR_NC}"
    log_info "3. Re-run setup: ${COLOR_CYAN}sudo ./docklite setup-ssh${COLOR_NC}"
fi

echo ""
log_info "Documentation: ${COLOR_CYAN}$(get_project_root)/SSH_ACCESS.md${COLOR_NC}"
echo ""
