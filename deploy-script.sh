#!/bin/bash
# deploy-script.sh - Run this on the remote server

set -e  # Exit on any error

DOCKER_REGISTRY=${1:-"your-dockerhub-username"}
REMOTE_HOST=${2:-"localhost"}  
echo "🚀 Starting deployment with registry: $DOCKER_REGISTRY"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo systemctl start docker
    sudo systemctl enable docker
    # Add current user to docker group to avoid needing sudo for docker commands
    sudo usermod -aG docker $USER
    newgrp docker
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create data directories
echo "📁 Creating data directories..."
sudo mkdir -p /var/ci_data/postgres/data
sudo mkdir -p /var/ci_data/nginx/logs
sudo mkdir -p /var/ci_data/mcp_server/logs

# Ensure PostgreSQL can access its data directory (UID 999 inside the container)
sudo chown -R 999:999 /var/ci_data/postgres

# The other directories can be owned by the deploying user
sudo chown -R $USER:$USER /var/ci_data/nginx/logs /var/ci_data/mcp_server/logs

# Update docker-compose.yml with correct registry/Remote_host
sed -i "s/\${DOCKER_REGISTRY}/$DOCKER_REGISTRY/g" docker-compose.yml
sed -i "s/\${REMOTE_HOST}/$REMOTE_HOST/g" docker-compose.yml

# Pull latest images
echo "📥 Pulling latest images..."
docker-compose pull

# Deploy services
echo "🏃 Starting services..."
docker-compose up -d

# Show status
echo "📊 Service Status:"
docker-compose ps

echo "✅ Deployment completed!"
echo "🌐 Access your app at: http://$(curl -s ifconfig.me)"