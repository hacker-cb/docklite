#!/bin/bash
# DockLite - Run All Tests
# Usage: ./test-all.sh [options]
#
# Options:
#   -h, --help      Show this help message
#   -v, --verbose   Verbose test output
#   -q, --quiet     Minimal output
#
# Examples:
#   ./test-all.sh           # Run all tests
#   ./test-all.sh --verbose # Detailed output

set -e

# Get script directory and source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$(dirname "$SCRIPT_DIR")/lib/common.sh"

# Show help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help "$0"
    exit 0
fi

print_banner "DockLite Test Suite"

# Parse options
VERBOSE=""
QUIET=""
if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
    VERBOSE="-v"
fi
if [ "$1" = "-q" ] || [ "$1" = "--quiet" ]; then
    QUIET="-q"
fi

# Change to project root
cd "$(get_project_root)"

BACKEND_EXIT=0
FRONTEND_EXIT=0

# Backend tests
echo ""
log_step "Running backend tests..."
if docker_compose_cmd run --rm backend pytest $VERBOSE $QUIET; then
    log_success "Backend tests passed"
    BACKEND_EXIT=0
else
    log_error "Backend tests failed"
    BACKEND_EXIT=1
fi

# Frontend tests
echo ""
log_step "Running frontend tests..."
cd frontend
if npm test -- --run; then
    log_success "Frontend tests passed"
    FRONTEND_EXIT=0
else
    log_error "Frontend tests failed"
    FRONTEND_EXIT=1
fi

# Summary
echo ""
print_banner "Test Summary"
if [ $BACKEND_EXIT -eq 0 ]; then
    log_success "Backend:  PASSED"
else
    log_error "Backend:  FAILED"
fi

if [ $FRONTEND_EXIT -eq 0 ]; then
    log_success "Frontend: PASSED"
else
    log_error "Frontend: FAILED"
fi

echo ""

# Exit with error if any tests failed
if [ $BACKEND_EXIT -ne 0 ] || [ $FRONTEND_EXIT -ne 0 ]; then
    log_error "Some tests failed"
    exit 1
fi

log_success "All tests passed! 🎉"
exit 0

