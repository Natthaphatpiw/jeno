#!/bin/bash

# Jetask Deployment Script for Ubuntu Server
# Usage: ./deploy.sh [dev|prod]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default environment
ENVIRONMENT=${1:-prod}

echo -e "${GREEN}🚀 Starting Jetask deployment in ${ENVIRONMENT} mode...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo -e "${YELLOW}⚠️  Please log out and log back in for Docker permissions to take effect${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Installing...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
sudo mkdir -p /var/log/jetask
sudo mkdir -p /tmp/jetask
sudo mkdir -p /var/uploads/jetask

# Set permissions
sudo chown -R $USER:$USER /var/log/jetask
sudo chown -R $USER:$USER /var/uploads/jetask

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${RED}📝 Please edit .env file with your API keys before continuing${NC}"
        exit 1
    else
        echo "OPENAI_API_KEY=your_openai_key_here" > .env
        echo -e "${RED}📝 Created .env file. Please add your OpenAI API key${NC}"
        exit 1
    fi
fi

# Stop existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose down --remove-orphans || true

# Clean up old images (optional)
echo -e "${YELLOW}🧹 Cleaning up old Docker images...${NC}"
docker system prune -f

# Build and start services
if [ "$ENVIRONMENT" = "prod" ]; then
    echo -e "${GREEN}🏗️  Building and starting production services...${NC}"
    docker-compose -f docker-compose.prod.yml up --build -d
else
    echo -e "${GREEN}🏗️  Building and starting development services...${NC}"
    docker-compose up --build -d
fi

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 30

# Check backend health
echo -e "${YELLOW}🔍 Checking backend health...${NC}"
for i in {1..10}; do
    if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
        break
    else
        if [ $i -eq 10 ]; then
            echo -e "${RED}❌ Backend health check failed${NC}"
            docker-compose logs backend
            exit 1
        fi
        echo "Attempt $i/10 - Backend not ready, waiting..."
        sleep 10
    fi
done

# Check frontend health
echo -e "${YELLOW}🔍 Checking frontend health...${NC}"
for i in {1..10}; do
    if curl -f http://localhost:3001/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is healthy${NC}"
        break
    else
        if [ $i -eq 10 ]; then
            echo -e "${RED}❌ Frontend health check failed${NC}"
            docker-compose logs frontend
            exit 1
        fi
        echo "Attempt $i/10 - Frontend not ready, waiting..."
        sleep 10
    fi
done

# Show running services
echo -e "${GREEN}📊 Running services:${NC}"
docker-compose ps

# Show logs (last 20 lines)
echo -e "${GREEN}📝 Recent logs:${NC}"
docker-compose logs --tail=20

# Final status
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Application is running at:${NC}"
echo -e "${GREEN}   Frontend: http://43.209.0.15:3001${NC}"
echo -e "${GREEN}   Backend:  http://43.209.0.15:5000${NC}"
echo -e "${GREEN}   API Docs: http://43.209.0.15:5000/docs${NC}"

if [ "$ENVIRONMENT" = "prod" ]; then
    echo -e "${GREEN}   Nginx:    http://43.209.0.15:80${NC}"
fi

echo -e "${YELLOW}📋 Useful commands:${NC}"
echo -e "${YELLOW}   View logs:    docker-compose logs -f${NC}"
echo -e "${YELLOW}   Stop:         docker-compose down${NC}"
echo -e "${YELLOW}   Restart:      docker-compose restart${NC}"
echo -e "${YELLOW}   Monitor:      docker stats${NC}"