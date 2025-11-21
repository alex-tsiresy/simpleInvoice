#!/bin/bash

# Check status of all services for Compass Document Processing

echo "Compass Document Processing - Service Status"
echo "=============================================="
echo ""

# Check OCR service
echo "1. OCR Microservice (Port 8119):"
if pgrep -f "python main.py" > /dev/null; then
    echo "   Status: ✓ Running"
    PID=$(pgrep -f "python main.py")
    echo "   PID: $PID"

    # Check health endpoint
    if curl -s http://localhost:8119/health > /dev/null 2>&1; then
        echo "   Health: ✓ Healthy"
    else
        echo "   Health: ✗ Not responding"
    fi
else
    echo "   Status: ✗ Not running"
fi

echo ""

# Check Docker containers
echo "2. Docker Containers:"

if ! docker ps > /dev/null 2>&1; then
    echo "   ERROR: Cannot connect to Docker daemon"
    exit 1
fi

# Backend
if docker ps | grep -q compass-backend; then
    echo "   Backend (8000):     ✓ Running"
else
    echo "   Backend (8000):     ✗ Not running"
fi

# Frontend
if docker ps | grep -q compass-frontend; then
    echo "   Frontend (3000):    ✓ Running"
else
    echo "   Frontend (3000):    ✗ Not running"
fi

# PostgreSQL
if docker ps | grep -q compass-postgres; then
    echo "   PostgreSQL (5432):  ✓ Running"
else
    echo "   PostgreSQL (5432):  ✗ Not running"
fi

# MinIO
if docker ps | grep -q compass-minio; then
    echo "   MinIO (9000):       ✓ Running"
else
    echo "   MinIO (9000):       ✗ Not running"
fi

echo ""

# Check connectivity
echo "3. Service Connectivity:"

# OCR service
if curl -s http://localhost:8119/health > /dev/null 2>&1; then
    echo "   OCR Service:        ✓ Accessible"
else
    echo "   OCR Service:        ✗ Not accessible"
fi

# Backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   Backend API:        ✓ Accessible"
else
    echo "   Backend API:        ✗ Not accessible"
fi

# Frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   Frontend:           ✓ Accessible"
else
    echo "   Frontend:           ✗ Not accessible"
fi

# MinIO
if curl -s http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    echo "   MinIO:              ✓ Accessible"
else
    echo "   MinIO:              ✗ Not accessible"
fi

echo ""

# Check GPU
echo "4. GPU Status:"
if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits)
    if [ -n "$GPU_INFO" ]; then
        echo "   GPU: ✓ Available"
        echo "   $GPU_INFO"
    else
        echo "   GPU: ✗ Not detected"
    fi
else
    echo "   nvidia-smi: ✗ Not available"
fi

echo ""
echo "=============================================="
echo ""
echo "To view logs:"
echo "  - OCR service:  tail -f ocr-service/ocr-service.log"
echo "  - Backend:      docker compose logs -f backend"
echo "  - All:          docker compose logs -f"
echo ""
