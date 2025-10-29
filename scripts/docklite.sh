#!/bin/bash
# DockLite - Main CLI Wrapper
# Usage: ./scripts/docklite.sh <command> [options]
#
# Commands:
#   Development:
#     start           Start DockLite services
#     stop            Stop DockLite services
#     restart         Restart DockLite services
#     rebuild         Rebuild and restart services
#     logs            Show container logs
#     test            Run all tests
#     test-backend    Run backend tests only
#     test-frontend   Run frontend tests only
#
#   Deployment:
#     setup-user      Create system user for deployment
#     setup-ssh       Configure SSH for localhost
#     init-db         Initialize database
#
#   Maintenance:
#     backup          Backup database and configuration
#     restore         Restore from backup
#     clean           Clean up unused resources
#     status          Show system status
#     reset-password  Reset user password
#
#   Setup:
#     install-completion  Install bash completion
#
#   Other:
#     version         Show DockLite version
#     help            Show this help message
#
# Examples:
#   ./scripts/docklite.sh start
#   ./scripts/docklite.sh test
#   ./scripts/docklite.sh setup-user
#   ./scripts/docklite.sh backup

set -e

# Get script directory
# Handle both direct execution and symlink
if [ -L "${BASH_SOURCE[0]}" ]; then
    SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
else
    SCRIPT_PATH="${BASH_SOURCE[0]}"
fi
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Source common functions
source "$SCRIPT_DIR/lib/common.sh"

# Show help if no command or --help
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ] || [ "$1" = "help" ]; then
    show_help "$0"
    exit 0
fi

# Get command
COMMAND=$1
shift

# Execute command
case "$COMMAND" in
    # Development commands
    start)
        exec "$SCRIPT_DIR/development/start.sh" "$@"
        ;;
    stop)
        exec "$SCRIPT_DIR/development/stop.sh" "$@"
        ;;
    restart)
        "$SCRIPT_DIR/development/stop.sh" "$@"
        "$SCRIPT_DIR/development/start.sh" "$@"
        ;;
    rebuild)
        exec "$SCRIPT_DIR/development/rebuild.sh" "$@"
        ;;
    logs)
        cd "$PROJECT_ROOT"
        docker_compose_cmd logs -f "$@"
        ;;
    test)
        exec "$SCRIPT_DIR/development/test-all.sh" "$@"
        ;;
    test-backend)
        exec "$SCRIPT_DIR/development/test-backend.sh" "$@"
        ;;
    test-frontend)
        exec "$SCRIPT_DIR/development/test-frontend.sh" "$@"
        ;;
    
    # Deployment commands
    setup-user)
        exec "$SCRIPT_DIR/deployment/setup-system-user.sh" "$@"
        ;;
    setup-ssh)
        exec "$SCRIPT_DIR/deployment/configure-ssh.sh" "$@"
        ;;
    init-db)
        exec "$SCRIPT_DIR/deployment/init-database.sh" "$@"
        ;;
    
    # Maintenance commands
    backup)
        exec "$SCRIPT_DIR/maintenance/backup.sh" "$@"
        ;;
    restore)
        exec "$SCRIPT_DIR/maintenance/restore.sh" "$@"
        ;;
    clean)
        exec "$SCRIPT_DIR/maintenance/clean.sh" "$@"
        ;;
    status)
        exec "$SCRIPT_DIR/maintenance/status.sh" "$@"
        ;;
    reset-password)
        exec "$SCRIPT_DIR/maintenance/reset-password.sh" "$@"
        ;;
    
    # Setup
    install-completion)
        exec "$SCRIPT_DIR/completion/install-completion.sh" "$@"
        ;;
    
    # Other
    version)
        echo "DockLite v$(get_docklite_version)"
        ;;
    
    *)
        log_error "Unknown command: $COMMAND"
        echo ""
        show_help "$0"
        exit 1
        ;;
esac

