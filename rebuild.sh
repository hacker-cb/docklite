#!/bin/bash
set -e

echo "Rebuilding DockLite..."

# Stop containers
docker-compose down

# Rebuild and start
docker-compose up -d --build

echo ""
echo "DockLite rebuilt and started!"
echo "Frontend: http://artem.sokolov.me:5173"
echo "Backend API: http://artem.sokolov.me:8000"
echo ""
echo "Run 'docker-compose logs -f' to see logs"

