#!/bin/bash

# Start all services for Compass Document Processing

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Starting Compass Document Processing System..."
echo "=============================================="
echo ""

# Check if OCR service venv exists
if [ ! -d "$PROJECT_ROOT/ocr-service/venv" ]; then
    echo "ERROR: OCR service venv not found!"
    echo "Please run: cd ocr-service && ./setup.sh"
    exit 1
fi

# Start OCR service in background
echo "1. Starting OCR microservice (port 8119)..."
cd "$PROJECT_ROOT/ocr-service"

# Check if already running
if pgrep -f "python main.py" > /dev/null; then
    echo "   OCR service is already running"
else
    nohup ./start.sh > ocr-service.log 2>&1 &
    OCR_PID=$!
    echo "   OCR service started (PID: $OCR_PID)"

    # Wait for OCR service to be ready
    echo "   Waiting for OCR service to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8119/health > /dev/null 2>&1; then
            echo "   ✓ OCR service is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "   WARNING: OCR service health check timeout"
        fi
        sleep 2
    done
fi

echo ""

# Start Docker containers
echo "2. Starting Docker containers..."
cd "$PROJECT_ROOT"

if docker ps | grep -q compass-backend; then
    echo "   Containers are already running"
else
    docker compose up -d
    echo "   ✓ Docker containers started"
fi

echo ""
echo "=============================================="
echo "All services started successfully!"
echo ""
echo "Services:"
echo "  - OCR Service:    http://localhost:8119"
echo "  - Backend API:    http://localhost:8000"
echo "  - Frontend:       http://localhost:3000"
echo "  - MinIO Console:  http://localhost:9001"
echo ""
echo "To view logs:"
echo "  - OCR service:    tail -f ocr-service/ocr-service.log"
echo "  - Backend:        docker compose logs -f backend"
echo "  - All containers: docker compose logs -f"
echo ""
echo "To stop all services:"
echo "  ./scripts/stop-all.sh"
echo ""
