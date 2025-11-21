#!/bin/bash

# Compass Document Processing - Setup Script
# This script automates the initial setup process

set -e

echo "=================================="
echo "Compass Document Processing Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}Error: This script is designed for Linux systems${NC}"
    exit 1
fi

# Check for required commands
echo "Checking prerequisites..."

command -v docker >/dev/null 2>&1 || {
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/engine/install/"
    exit 1
}

if ! docker compose version >/dev/null 2>&1; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check for NVIDIA GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${YELLOW}Warning: nvidia-smi not found. GPU may not be available.${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
fi

# Check for NVIDIA Container Toolkit
if ! docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo -e "${YELLOW}Warning: NVIDIA Container Toolkit not properly configured${NC}"
    read -p "Would you like to install it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing NVIDIA Container Toolkit..."
        distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
        curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
        curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
          sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
          sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
        sudo apt-get update
        sudo apt-get install -y nvidia-container-toolkit
        sudo nvidia-ctk runtime configure --runtime=docker
        sudo systemctl restart docker
        echo -e "${GREEN}✓ NVIDIA Container Toolkit installed${NC}"
    fi
else
    echo -e "${GREEN}✓ NVIDIA Container Toolkit configured${NC}"
fi

# Setup environment files
echo ""
echo "Setting up environment files..."

if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and add your Clerk and OpenAI API keys${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    echo -e "${GREEN}✓ Created frontend/.env file${NC}"
    echo -e "${YELLOW}⚠ Please edit frontend/.env and add your Clerk Publishable Key${NC}"
else
    echo -e "${GREEN}✓ frontend/.env file already exists${NC}"
fi

# Build and start services
echo ""
echo "Building and starting Docker services..."
read -p "Would you like to start the services now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Building Docker images (this may take a while)..."
    docker compose build

    echo "Starting services..."
    docker compose up -d

    echo ""
    echo "Waiting for services to be ready..."
    sleep 10

    # Check service health
    echo ""
    echo "Checking service health..."

    if curl -sf http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✓ Backend API: healthy${NC}"
    else
        echo -e "${RED}✗ Backend API: not responding${NC}"
    fi

    if curl -sf http://localhost:8118/health > /dev/null; then
        echo -e "${GREEN}✓ PaddleOCR: healthy${NC}"
    else
        echo -e "${YELLOW}⚠ PaddleOCR: not responding (may take a few minutes to start)${NC}"
    fi

    echo ""
    echo -e "${GREEN}Setup complete!${NC}"
    echo ""
    echo "Services are available at:"
    echo "  - Frontend:    http://localhost:3000"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Docs:    http://localhost:8000/docs"
    echo "  - MinIO:       http://localhost:9001"
    echo ""
    echo "To view logs: docker compose logs -f"
    echo "To stop:      docker compose down"
else
    echo ""
    echo "Setup complete! To start services later, run:"
    echo "  docker compose up -d"
fi
