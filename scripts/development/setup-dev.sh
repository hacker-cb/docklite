#!/bin/bash
# DockLite Development Setup Script
# Sets up development environment (Python dependencies, env file)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$SCRIPT_DIR/../lib/common.sh"

log_header "DockLite Development Setup"

# Check Python
log_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is required but not installed"
    echo "Install Python 3.8+ and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_success "Python $PYTHON_VERSION found"

# Create virtual environment
VENV_DIR="$PROJECT_ROOT/.venv"
if [ ! -d "$VENV_DIR" ]; then
    log_info "Creating virtual environment..."
    if python3 -m venv "$VENV_DIR"; then
        log_success "Virtual environment created at .venv/"
    else
        log_error "Failed to create virtual environment"
        echo "Make sure python3-venv is installed:"
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            echo "  sudo apt-get install python3-venv"
        fi
        exit 1
    fi
else
    log_success "Virtual environment already exists"
fi

# Install Python CLI dependencies in venv
log_info "Installing Python CLI dependencies in venv..."
cd "$PROJECT_ROOT"

if "$VENV_DIR/bin/pip" install -q -r scripts/requirements.txt; then
    log_success "CLI dependencies installed in venv"
else
    log_error "Failed to install CLI dependencies"
    echo "Try manually: .venv/bin/pip install -r scripts/requirements.txt"
    exit 1
fi

# Check .env file
log_info "Checking .env configuration..."
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        log_info "Creating .env from .env.example..."
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        log_success ".env file created"
        echo ""
        log_warning "Please edit .env and set your HOSTNAME:"
        echo "  nano .env"
    else
        log_warning "No .env.example found"
        echo "Create .env manually with required settings"
    fi
else
    log_success ".env file exists"
fi

# Check Docker
log_info "Checking Docker..."
if ! command -v docker &> /dev/null; then
    log_warning "Docker is not installed or not running"
    echo "Install Docker Desktop (macOS) or Docker Engine (Linux)"
    echo "See: https://docs.docker.com/get-docker/"
else
    if docker info &> /dev/null; then
        log_success "Docker is running"
    else
        log_warning "Docker is installed but not running"
        echo "Start Docker Desktop or Docker service"
    fi
fi

# Check docker-compose
log_info "Checking Docker Compose..."
if docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version --short)
    log_success "Docker Compose $COMPOSE_VERSION found"
else
    log_warning "Docker Compose V2 not found"
    echo "Install Docker Compose V2 or use Docker Desktop"
fi

# Make docklite executable
log_info "Making docklite CLI executable..."
chmod +x "$PROJECT_ROOT/docklite"
chmod +x "$PROJECT_ROOT/scripts/docklite.sh"
log_success "CLI ready"

echo ""
log_header "Setup Complete! 🎉"
echo ""
echo "Next steps:"
echo "  1. Edit .env file:        nano .env"
echo "  2. Start DockLite:        ./docklite start"
echo "  3. Create admin user:     ./docklite add-user admin -p 'YourPassword' --admin"
echo "  4. Open in browser:       $(get_access_url)"
echo ""
echo "Available commands:"
echo "  ./docklite --help         # Show all commands"
echo "  ./docklite status         # Check system status"
echo "  ./docklite test           # Run all tests"
echo ""

