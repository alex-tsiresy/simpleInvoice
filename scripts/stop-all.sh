#!/bin/bash

# Stop all services for Compass Document Processing

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Stopping Compass Document Processing System..."
echo "=============================================="
echo ""

# Stop Docker containers
echo "1. Stopping Docker containers..."
cd "$PROJECT_ROOT"

if docker ps | grep -q compass-backend; then
    docker compose down
    echo "   ✓ Docker containers stopped"
else
    echo "   Containers are not running"
fi

echo ""

# Stop OCR service
echo "2. Stopping OCR microservice..."

if pgrep -f "python main.py" > /dev/null; then
    pkill -f "python main.py"
    echo "   ✓ OCR service stopped"
else
    echo "   OCR service is not running"
fi

echo ""
echo "=============================================="
echo "All services stopped"
echo ""
