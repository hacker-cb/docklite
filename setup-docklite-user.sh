#!/bin/bash
set -e

echo "🔧 Setting up DockLite deployment user"
echo "======================================"

# Configuration (can be customized)
DEPLOY_USER="${DEPLOY_USER:-docklite}"
PROJECTS_DIR="${PROJECTS_DIR:-/home/$DEPLOY_USER/projects}"
DEPLOY_USER_SHELL="${DEPLOY_USER_SHELL:-/bin/bash}"

echo "User: $DEPLOY_USER"
echo "Projects directory: $PROJECTS_DIR"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

# Create user if doesn't exist
if id "$DEPLOY_USER" &>/dev/null; then
    echo "✅ User '$DEPLOY_USER' already exists"
else
    echo "📝 Creating user '$DEPLOY_USER'..."
    useradd -m -s "$DEPLOY_USER_SHELL" -d "/home/$DEPLOY_USER" "$DEPLOY_USER"
    echo "✅ User created"
fi

# Create projects directory
echo "📁 Creating projects directory..."
mkdir -p "$PROJECTS_DIR"
chown -R "$DEPLOY_USER:$DEPLOY_USER" "$PROJECTS_DIR"
chmod 755 "$PROJECTS_DIR"
echo "✅ Projects directory: $PROJECTS_DIR"

# Create .ssh directory for SSH keys
echo "🔐 Setting up SSH access..."
SSH_DIR="/home/$DEPLOY_USER/.ssh"
mkdir -p "$SSH_DIR"
touch "$SSH_DIR/authorized_keys"
chown -R "$DEPLOY_USER:$DEPLOY_USER" "$SSH_DIR"
chmod 700 "$SSH_DIR"
chmod 600 "$SSH_DIR/authorized_keys"
echo "✅ SSH directory configured"

# Add pavel to docklite group (for docker-compose access)
if [ "$DEPLOY_USER" != "pavel" ]; then
    echo "👥 Adding 'pavel' to '$DEPLOY_USER' group..."
    usermod -a -G "$DEPLOY_USER" pavel
    usermod -a -G docker "$DEPLOY_USER"
    echo "✅ Groups configured"
fi

# Update .env file
ENV_FILE="/home/pavel/docklite/.env"
if [ -f "$ENV_FILE" ]; then
    echo "⚙️  Updating .env configuration..."
    
    # Backup original
    cp "$ENV_FILE" "$ENV_FILE.backup"
    
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
    
    echo "✅ Configuration updated"
    echo "   Backup saved: $ENV_FILE.backup"
fi

# Create info file
INFO_FILE="/home/$DEPLOY_USER/README.txt"
cat > "$INFO_FILE" << EOF
DockLite Deployment User
========================

This user is for deploying applications to DockLite.

Projects Directory: $PROJECTS_DIR
Each project has its own subdirectory: $PROJECTS_DIR/{project_id}/

SSH Access:
-----------
1. Add your SSH public key to: /home/$DEPLOY_USER/.ssh/authorized_keys
2. Use rsync/scp to upload files:
   
   rsync -avz ./my-app/ $DEPLOY_USER@server:$PROJECTS_DIR/{project_id}/
   
3. Deploy with docker-compose:
   
   ssh $DEPLOY_USER@server "cd $PROJECTS_DIR/{project_id} && docker-compose up -d"

For more information, see: /home/pavel/docklite/SSH_ACCESS.md
EOF

chown "$DEPLOY_USER:$DEPLOY_USER" "$INFO_FILE"
echo "✅ Info file created: $INFO_FILE"

echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Add SSH keys: sudo -u $DEPLOY_USER nano /home/$DEPLOY_USER/.ssh/authorized_keys"
echo "2. Test connection: ssh $DEPLOY_USER@localhost"
echo "3. Restart DockLite: cd /home/pavel/docklite && ./rebuild.sh"
echo ""
echo "📖 Documentation: /home/pavel/docklite/SSH_ACCESS.md"

