#!/bin/bash
# DockLite - Create System User for Deployment
# Usage: ./setup-system-user.sh [options]
#
# Options:
#   -h, --help      Show this help message
#   -u, --user      Username (default: docklite)
#   -d, --dir       Projects directory (default: /home/{user}/projects)
#
# Examples:
#   sudo ./setup-system-user.sh                    # Create 'docklite' user
#   sudo ./setup-system-user.sh -u myuser          # Create 'myuser'
#   sudo DEPLOY_USER=custom ./setup-system-user.sh # Via env var

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

# Configuration (can be customized)
DEPLOY_USER="${DEPLOY_USER:-docklite}"
PROJECTS_DIR="${PROJECTS_DIR:-/home/$DEPLOY_USER/projects}"
DEPLOY_USER_SHELL="${DEPLOY_USER_SHELL:-/bin/bash}"

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--user)
            DEPLOY_USER="$2"
            PROJECTS_DIR="/home/$DEPLOY_USER/projects"
            shift 2
            ;;
        -d|--dir)
            PROJECTS_DIR="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

print_banner "Setting up DockLite Deployment User"

log_info "User: ${COLOR_CYAN}$DEPLOY_USER${COLOR_NC}"
log_info "Projects directory: ${COLOR_CYAN}$PROJECTS_DIR${COLOR_NC}"
echo ""

# Create user if doesn't exist
log_step "Checking user..."
if user_exists "$DEPLOY_USER"; then
    log_success "User '$DEPLOY_USER' already exists"
else
    log_step "Creating user '$DEPLOY_USER'..."
    useradd -m -s "$DEPLOY_USER_SHELL" -d "/home/$DEPLOY_USER" "$DEPLOY_USER"
    log_success "User created"
fi

# Unlock account if locked
if passwd -S "$DEPLOY_USER" | grep -q " L "; then
    log_step "Unlocking account..."
    usermod -p '*' "$DEPLOY_USER"
    log_success "Account unlocked"
fi

# Create projects directory
log_step "Creating projects directory..."
mkdir -p "$PROJECTS_DIR"
chown -R "$DEPLOY_USER:$DEPLOY_USER" "$PROJECTS_DIR"
chmod 755 "$PROJECTS_DIR"
log_success "Projects directory: $PROJECTS_DIR"

# Create .ssh directory for SSH keys
log_step "Setting up SSH access..."
SSH_DIR="/home/$DEPLOY_USER/.ssh"
mkdir -p "$SSH_DIR"
touch "$SSH_DIR/authorized_keys"
chown -R "$DEPLOY_USER:$DEPLOY_USER" "$SSH_DIR"
chmod 700 "$SSH_DIR"
chmod 600 "$SSH_DIR/authorized_keys"
log_success "SSH directory configured"

# Add to docker group
log_step "Adding to docker group..."
usermod -aG docker "$DEPLOY_USER"
log_success "Docker access granted"

# Add current user to deploy user group (if different)
ACTUAL_USER=$(get_actual_user)
if [ "$DEPLOY_USER" != "$ACTUAL_USER" ]; then
    log_step "Adding '$ACTUAL_USER' to '$DEPLOY_USER' group..."
    usermod -aG "$DEPLOY_USER" "$ACTUAL_USER"
    log_success "Groups configured"
fi

# Update .env file
ENV_FILE="$(get_project_root)/.env"
if [ -f "$ENV_FILE" ]; then
    log_step "Updating .env configuration..."
    
    # Backup original
    backup_file "$ENV_FILE"
    
    # Update PROJECTS_DIR
    if grep -q "^PROJECTS_DIR=" "$ENV_FILE"; then
        sed -i "s|^PROJECTS_DIR=.*|PROJECTS_DIR=$PROJECTS_DIR|" "$ENV_FILE"
    else
        echo "PROJECTS_DIR=$PROJECTS_DIR" >> "$ENV_FILE"
    fi
    
    # Update DEPLOY_USER  
    if grep -q "^DEPLOY_USER=" "$ENV_FILE"; then
        sed -i "s|^DEPLOY_USER=.*|DEPLOY_USER=$DEPLOY_USER|" "$ENV_FILE"
    else
        echo "DEPLOY_USER=$DEPLOY_USER" >> "$ENV_FILE"
    fi
    
    log_success "Configuration updated"
fi

# Create info file
INFO_FILE="/home/$DEPLOY_USER/README.txt"
cat > "$INFO_FILE" << EOF
DockLite Deployment User
========================

This user is for deploying applications to DockLite.

User: $DEPLOY_USER
Projects Directory: $PROJECTS_DIR

Project paths: $PROJECTS_DIR/{project-slug}/

SSH Access:
-----------
1. Add your SSH public key to: /home/$DEPLOY_USER/.ssh/authorized_keys
2. Use rsync/scp to upload files:
   
   rsync -avz ./my-app/ $DEPLOY_USER@server:$PROJECTS_DIR/{project-slug}/
   
3. Deploy with docker-compose:
   
   ssh $DEPLOY_USER@server "cd $PROJECTS_DIR/{project-slug} && docker-compose up -d"

For more information, see: $(get_project_root)/SSH_ACCESS.md
EOF

chown "$DEPLOY_USER:$DEPLOY_USER" "$INFO_FILE"
log_success "Info file created: $INFO_FILE"

echo ""
print_banner "Setup Complete!"
echo ""
log_info "Next steps:"
log_info "1. Configure SSH: ${COLOR_CYAN}sudo ./docklite setup-ssh${COLOR_NC}"
log_info "2. Start DockLite: ${COLOR_CYAN}./docklite start${COLOR_NC}"
log_info "3. Access UI: ${COLOR_CYAN}http://localhost:5173${COLOR_NC}"
echo ""
log_info "Documentation: ${COLOR_CYAN}$(get_project_root)/SSH_ACCESS.md${COLOR_NC}"
echo ""
