#!/bin/bash
set -e

echo "Starting DockLite..."

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running"
    exit 1
fi

# Create projects directory if not exists
mkdir -p /home/pavel/docklite-projects

# Start services
docker-compose up -d --build

echo ""
echo "DockLite is starting..."
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Run 'docker-compose logs -f' to see logs"
