#!/bin/bash
# DockLite - Run Frontend Tests
# Usage: ./test-frontend.sh [options]
#
# Options:
#   -h, --help      Show this help message
#   -w, --watch     Watch mode
#   -u, --ui        Open UI
#   --coverage      Show coverage report
#
# Examples:
#   ./test-frontend.sh           # Run all tests
#   ./test-frontend.sh --watch   # Watch mode
#   ./test-frontend.sh --ui      # Interactive UI

set -e

# Get script directory and source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$(dirname "$SCRIPT_DIR")/lib/common.sh"

# Show help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help "$0"
    exit 0
fi

print_banner "Frontend Tests (Vitest)"

# Change to frontend directory
cd "$(get_project_root)/frontend"

# Check node_modules
if [ ! -d "node_modules" ]; then
    log_warning "node_modules not found. Installing dependencies..."
    npm install
fi

# Run tests
log_step "Running frontend tests..."
if [ "$1" = "-w" ] || [ "$1" = "--watch" ]; then
    npm test
elif [ "$1" = "-u" ] || [ "$1" = "--ui" ]; then
    npm test -- --ui
else
    npm test -- --run "$@"
fi

log_success "Frontend tests complete"

