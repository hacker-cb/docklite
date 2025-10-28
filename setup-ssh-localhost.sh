#!/bin/bash
set -e

echo "🔐 DockLite SSH Setup for Localhost"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

DEPLOY_USER="docklite"
DEPLOY_HOME="/home/$DEPLOY_USER"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ This script must be run as root${NC}"
    echo "   Run: sudo ./setup-ssh-localhost.sh"
    exit 1
fi

# Determine the actual user (who ran sudo)
ACTUAL_USER="${SUDO_USER:-$USER}"
if [ "$ACTUAL_USER" = "root" ]; then
    echo -e "${RED}❌ Cannot determine actual user. Please run with: sudo -u pavel ./setup-ssh-localhost.sh${NC}"
    exit 1
fi

ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)
SSH_KEY="$ACTUAL_HOME/.ssh/id_ed25519"

echo "👤 Actual user: $ACTUAL_USER"
echo "🏠 Deploy user: $DEPLOY_USER"
echo "🔑 SSH key will be: $SSH_KEY"
echo ""

# Step 1: Ensure docklite user exists and is unlocked
echo "1️⃣  Checking docklite user..."
if id "$DEPLOY_USER" &>/dev/null; then
    echo -e "${GREEN}✅ User '$DEPLOY_USER' exists${NC}"
    
    # Check if account is locked
    if passwd -S "$DEPLOY_USER" | grep -q " L "; then
        echo "   🔓 Unlocking account..."
        usermod -p '*' "$DEPLOY_USER"
        echo -e "${GREEN}✅ Account unlocked${NC}"
    else
        echo "   ✅ Account is already unlocked"
    fi
else
    echo -e "${RED}❌ User '$DEPLOY_USER' doesn't exist. Run ./setup-docklite-user.sh first${NC}"
    exit 1
fi

# Step 2: Fix ~/.ssh permissions for actual user
echo ""
echo "2️⃣  Fixing ~/.ssh permissions for $ACTUAL_USER..."
if [ -d "$ACTUAL_HOME/.ssh" ]; then
    chown -R $ACTUAL_USER:$ACTUAL_USER "$ACTUAL_HOME/.ssh"
    chmod 700 "$ACTUAL_HOME/.ssh"
    echo -e "${GREEN}✅ Permissions fixed${NC}"
else
    mkdir -p "$ACTUAL_HOME/.ssh"
    chown $ACTUAL_USER:$ACTUAL_USER "$ACTUAL_HOME/.ssh"
    chmod 700 "$ACTUAL_HOME/.ssh"
    echo -e "${GREEN}✅ Created ~/.ssh${NC}"
fi

# Step 3: Generate SSH key if doesn't exist
echo ""
echo "3️⃣  Checking SSH key..."
if [ -f "$SSH_KEY" ]; then
    echo -e "${YELLOW}⚠️  SSH key already exists: $SSH_KEY${NC}"
    echo "   Using existing key."
else
    echo "Generating new SSH key for $ACTUAL_USER..."
    sudo -u $ACTUAL_USER ssh-keygen -t ed25519 -C "docklite@localhost" -f "$SSH_KEY" -N ""
    echo -e "${GREEN}✅ SSH key created: $SSH_KEY${NC}"
fi

# Ensure key has correct permissions
chmod 600 "$SSH_KEY"
chmod 644 "$SSH_KEY.pub"
chown $ACTUAL_USER:$ACTUAL_USER "$SSH_KEY" "$SSH_KEY.pub"

# Step 4: Ensure docklite .ssh directory exists with correct permissions
echo ""
echo "4️⃣  Setting up docklite .ssh directory..."
mkdir -p "$DEPLOY_HOME/.ssh"
chmod 700 "$DEPLOY_HOME/.ssh"
chown -R $DEPLOY_USER:$DEPLOY_USER "$DEPLOY_HOME/.ssh"
echo -e "${GREEN}✅ Directory configured${NC}"

# Step 5: Add public key to authorized_keys
echo ""
echo "5️⃣  Adding SSH key to authorized_keys..."
PUBKEY=$(cat "$SSH_KEY.pub")

# Check if key already exists
if grep -q "$PUBKEY" "$DEPLOY_HOME/.ssh/authorized_keys" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Key already in authorized_keys${NC}"
else
    echo "$PUBKEY" >> "$DEPLOY_HOME/.ssh/authorized_keys"
    echo -e "${GREEN}✅ Key added to authorized_keys${NC}"
fi

# Step 6: Fix authorized_keys permissions
echo ""
echo "6️⃣  Fixing authorized_keys permissions..."
chmod 600 "$DEPLOY_HOME/.ssh/authorized_keys"
chown $DEPLOY_USER:$DEPLOY_USER "$DEPLOY_HOME/.ssh/authorized_keys"
echo -e "${GREEN}✅ Permissions set (600)${NC}"

# Step 7: Ensure projects directory exists
echo ""
echo "7️⃣  Checking projects directory..."
mkdir -p "$DEPLOY_HOME/projects"
chown -R $DEPLOY_USER:$DEPLOY_USER "$DEPLOY_HOME/projects"
chmod 755 "$DEPLOY_HOME/projects"
echo -e "${GREEN}✅ Projects directory ready: $DEPLOY_HOME/projects${NC}"

# Step 8: Check SSH server configuration
echo ""
echo "8️⃣  Checking SSH server configuration..."
if grep -q "^PubkeyAuthentication yes" /etc/ssh/sshd_config; then
    echo -e "${GREEN}✅ PubkeyAuthentication is enabled${NC}"
elif grep -q "^PubkeyAuthentication no" /etc/ssh/sshd_config; then
    echo -e "${RED}❌ PubkeyAuthentication is DISABLED${NC}"
    echo "   Enabling PubkeyAuthentication..."
    sed -i 's/^PubkeyAuthentication no/PubkeyAuthentication yes/' /etc/ssh/sshd_config
    systemctl restart sshd
    echo -e "${GREEN}✅ PubkeyAuthentication enabled and sshd restarted${NC}"
else
    echo -e "${YELLOW}⚠️  PubkeyAuthentication not explicitly set (usually defaults to yes)${NC}"
fi

# Step 9: Test SSH connection
echo ""
echo "9️⃣  Testing SSH connection..."
echo "   Trying: ssh -o StrictHostKeyChecking=no -o BatchMode=yes $DEPLOY_USER@localhost 'echo OK'"

if sudo -u $ACTUAL_USER ssh -o StrictHostKeyChecking=no -o BatchMode=yes $DEPLOY_USER@localhost 'echo OK' 2>/dev/null | grep -q "OK"; then
    echo -e "${GREEN}✅ SSH connection successful!${NC}"
    SSH_OK=true
else
    echo -e "${RED}❌ SSH connection failed${NC}"
    echo ""
    echo "Testing connection with verbose output..."
    sudo -u $ACTUAL_USER ssh -o StrictHostKeyChecking=no $DEPLOY_USER@localhost 'echo OK' 2>&1 | tail -20
    SSH_OK=false
fi

# Step 10: Test docker-compose and docker access
if [ "$SSH_OK" = true ]; then
    echo ""
    echo "🔟  Testing docker-compose access..."
    if sudo -u $ACTUAL_USER ssh $DEPLOY_USER@localhost 'which docker-compose' &>/dev/null; then
        echo -e "${GREEN}✅ docker-compose is accessible${NC}"
    else
        echo -e "${RED}❌ docker-compose not found${NC}"
    fi
    
    # Test docker access
    echo ""
    echo "1️⃣1️⃣  Testing docker access..."
    if sudo -u $ACTUAL_USER ssh $DEPLOY_USER@localhost 'docker ps' &>/dev/null; then
        echo -e "${GREEN}✅ Docker is accessible (user in docker group)${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker not accessible, adding $DEPLOY_USER to docker group...${NC}"
        usermod -aG docker $DEPLOY_USER
        echo -e "${GREEN}✅ Added to docker group${NC}"
        echo "   Note: You may need to restart DockLite for group changes to take effect"
    fi
fi

# Summary
echo ""
echo "===================================="
echo "📊 Setup Summary"
echo "===================================="
echo "Actual user: $ACTUAL_USER"
echo "Deploy user: $DEPLOY_USER"
echo "SSH key: $SSH_KEY"
echo "Projects dir: $DEPLOY_HOME/projects"
echo ""

if [ "$SSH_OK" = true ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Rebuild DockLite: cd /home/pavel/docklite && ./rebuild.sh"
    echo "  2. Open admin UI: http://localhost:3000"
    echo "  3. Create nginx hello-world project"
    echo "  4. Click 'Start' button to test container management"
    echo "  5. Check logs: sg docker -c 'docker-compose logs -f backend'"
    echo ""
    echo -e "${GREEN}🎉 You're ready to deploy containers!${NC}"
else
    echo -e "${RED}❌ SSH setup incomplete${NC}"
    echo ""
    echo "Manual debugging:"
    echo "  1. Test as $ACTUAL_USER: su - $ACTUAL_USER -c 'ssh $DEPLOY_USER@localhost'"
    echo "  2. Check SSH server: systemctl status sshd"
    echo "  3. Check permissions:"
    echo "     - ls -la $DEPLOY_HOME/.ssh/"
    echo "     - ls -la $ACTUAL_HOME/.ssh/"
    echo "  4. View SSH logs: journalctl -u sshd -n 50"
fi

echo ""

