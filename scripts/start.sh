#!/bin/bash

# Start all services

echo "Starting Compass Document Processing services..."

docker compose up -d

echo ""
echo "Services starting..."
echo "This may take a few minutes, especially for PaddleOCR-VL."
echo ""
echo "Check status with: docker compose ps"
echo "View logs with:    docker compose logs -f"
echo ""
echo "Services will be available at:"
echo "  - Frontend:    http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - MinIO:       http://localhost:9001"
