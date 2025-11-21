#!/bin/bash

# Stop all services

echo "Stopping Compass Document Processing services..."

docker compose down

echo ""
echo "All services stopped."
echo ""
echo "To start again: ./scripts/start.sh"
echo "To remove volumes: docker compose down -v"
