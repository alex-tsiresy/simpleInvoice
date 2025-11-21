#!/bin/bash
# Switch from Docker Desktop to Docker CE (Engine)
# Run with: sudo bash switch-to-docker-ce.sh

set -e

echo "=========================================="
echo "Switching to Docker CE (Engine)"
echo "=========================================="
echo ""

# Stop Docker Desktop if running
echo "Stopping Docker Desktop..."
systemctl stop docker 2>/dev/null || true
killall "Docker Desktop" 2>/dev/null || true

echo ""
echo "Note: Please quit Docker Desktop from the system tray if it's running"
echo "Press Enter when you've quit Docker Desktop..."
read

echo ""
echo "Removing Docker Desktop packages..."
apt-get remove -y docker-desktop docker-desktop-data 2>/dev/null || true

echo ""
echo "Installing Docker CE..."

# Remove old Docker packages
apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Install prerequisites
apt-get update
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo ""
echo "Configuring Docker with NVIDIA runtime..."

# Configure Docker daemon for NVIDIA
cat > /etc/docker/daemon.json <<'EOF'
{
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
EOF

# Configure NVIDIA runtime
nvidia-ctk runtime configure --runtime=docker

# Add current user to docker group
CURRENT_USER=$(logname)
usermod -aG docker $CURRENT_USER

echo ""
echo "Starting Docker service..."
systemctl daemon-reload
systemctl enable docker
systemctl start docker

# Generate CDI config
echo ""
echo "Generating NVIDIA CDI configuration..."
mkdir -p /etc/cdi
nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml

sleep 3

echo ""
echo "=========================================="
echo "Testing Docker and GPU..."
echo "=========================================="
echo ""

# Test Docker
if systemctl is-active --quiet docker; then
    echo "✅ Docker service is running"
else
    echo "❌ Docker service failed to start"
    systemctl status docker --no-pager
    exit 1
fi

# Test GPU access
if docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi; then
    echo ""
    echo "✅ GPU access works!"
else
    echo "❌ GPU test failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Docker CE installed successfully!"
echo "=========================================="
echo ""
echo "Important: You need to log out and log back in for group changes to take effect"
echo ""
echo "After logging back in, you can run Docker without sudo:"
echo "  docker ps"
echo ""
echo "Then start Compass:"
echo "  cd /home/alex/compassDemo"
echo "  docker compose up -d"
echo ""
