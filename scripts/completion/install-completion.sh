#!/bin/bash
# DockLite - Install Bash Completion
# Usage: ./install-completion.sh [options]
#
# Options:
#   -h, --help      Show this help message
#   --global        Install globally (requires root, /etc/bash_completion.d/)
#   --local         Install locally (default, ~/.bash_completion)
#   --uninstall     Remove completion
#
# Examples:
#   ./install-completion.sh              # Install for current user
#   sudo ./install-completion.sh --global # Install for all users
#   ./install-completion.sh --uninstall   # Remove completion

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPLETION_FILE="$SCRIPT_DIR/docklite-completion.bash"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Show help
show_help() {
    sed -n '/^# Usage:/,/^$/p' "$0" | sed 's/^# *//'
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

# Parse options
MODE="local"
UNINSTALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --global)
            MODE="global"
            shift
            ;;
        --local)
            MODE="local"
            shift
            ;;
        --uninstall)
            UNINSTALL=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

echo "╔════════════════════════════════════════════════════════════╗"
echo "║ DockLite Bash Completion Installer                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Uninstall mode
if [ "$UNINSTALL" = true ]; then
    echo -e "${YELLOW}Uninstalling bash completion...${NC}"
    
    # Remove from local
    if [ -f "$HOME/.bash_completion" ] && grep -q "docklite-completion.bash" "$HOME/.bash_completion"; then
        sed -i '/docklite-completion.bash/d' "$HOME/.bash_completion"
        echo -e "${GREEN}✅${NC} Removed from ~/.bash_completion"
    fi
    
    # Remove from bashrc
    if [ -f "$HOME/.bashrc" ] && grep -q "docklite-completion.bash" "$HOME/.bashrc"; then
        sed -i '/docklite-completion.bash/d' "$HOME/.bashrc"
        echo -e "${GREEN}✅${NC} Removed from ~/.bashrc"
    fi
    
    # Remove global (if root)
    if [ "$EUID" -eq 0 ] && [ -f "/etc/bash_completion.d/docklite" ]; then
        rm -f /etc/bash_completion.d/docklite
        echo -e "${GREEN}✅${NC} Removed from /etc/bash_completion.d/"
    fi
    
    echo ""
    echo -e "${GREEN}✅ Completion uninstalled!${NC}"
    echo -e "${CYAN}Reload shell: source ~/.bashrc${NC}"
    exit 0
fi

# Install mode
if [ "$MODE" = "global" ]; then
    # Global installation (requires root)
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}❌ Global installation requires root${NC}"
        echo "   Run: sudo ./install-completion.sh --global"
        exit 1
    fi
    
    echo -e "${CYAN}Installing globally for all users...${NC}"
    
    # Copy to /etc/bash_completion.d/
    cp "$COMPLETION_FILE" /etc/bash_completion.d/docklite
    chmod 644 /etc/bash_completion.d/docklite
    
    echo -e "${GREEN}✅${NC} Installed to: /etc/bash_completion.d/docklite"
    echo ""
    echo -e "${GREEN}✅ Global installation complete!${NC}"
    echo -e "${YELLOW}Note:${NC} All users need to reload their shells"
    echo -e "${CYAN}Each user should run: source ~/.bashrc${NC}"
    
else
    # Local installation (default)
    echo -e "${CYAN}Installing for current user ($USER)...${NC}"
    
    # Add to ~/.bashrc if not already there
    BASHRC="$HOME/.bashrc"
    SOURCE_LINE="source \"$COMPLETION_FILE\""
    
    if grep -q "docklite-completion.bash" "$BASHRC" 2>/dev/null; then
        echo -e "${YELLOW}⚠️${NC}  Already installed in ~/.bashrc"
    else
        echo "" >> "$BASHRC"
        echo "# DockLite CLI completion" >> "$BASHRC"
        echo "$SOURCE_LINE" >> "$BASHRC"
        echo -e "${GREEN}✅${NC} Added to: ~/.bashrc"
    fi
    
    echo ""
    echo -e "${GREEN}✅ Local installation complete!${NC}"
    echo ""
    echo -e "${CYAN}To activate completion, run:${NC}"
    echo -e "  source ~/.bashrc"
    echo ""
    echo -e "${CYAN}Or in current shell:${NC}"
    echo -e "  source \"$COMPLETION_FILE\""
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║ Usage Examples                                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "After reloading shell, try:"
echo ""
echo -e "  ${CYAN}./docklite <TAB><TAB>${NC}         # Show all commands"
echo -e "  ${CYAN}./docklite st<TAB>${NC}            # Auto-complete 'start' or 'status'"
echo -e "  ${CYAN}./docklite start --<TAB><TAB>${NC} # Show start options"
echo -e "  ${CYAN}./docklite logs <TAB><TAB>${NC}    # Show services (backend/frontend)"
echo -e "  ${CYAN}./docklite restore <TAB>${NC}      # Complete .tar.gz files"
echo ""

