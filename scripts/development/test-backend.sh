#!/bin/bash
# DockLite - Run Backend Tests
# Usage: ./test-backend.sh [options]
#
# Options:
#   -h, --help      Show this help message
#   -v, --verbose   Verbose test output
#   -k PATTERN      Run tests matching pattern
#   --cov           Show coverage report
#
# Examples:
#   ./test-backend.sh                    # Run all tests
#   ./test-backend.sh --verbose          # Detailed output
#   ./test-backend.sh -k test_auth       # Run auth tests only
#   ./test-backend.sh --cov              # With coverage

set -e

# Get script directory and source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$(dirname "$SCRIPT_DIR")/lib/common.sh"

# Show help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help "$0"
    exit 0
fi

print_banner "Backend Tests (Python/Pytest)"

# Change to project root
cd "$(get_project_root)"

# Run tests in Docker
log_step "Running backend tests..."
docker_compose_cmd run --rm backend pytest "$@"

log_success "Backend tests complete"

