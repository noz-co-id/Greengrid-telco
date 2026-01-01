#!/bin/bash
# quickstart.sh
# One-command deployment untuk Greengrid Telco

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   Greengrid Telco Quick Start Setup    ║"
echo "╔════════════════════════════════════════╗"
echo -e "${NC}"

# Check Docker
echo -e "${YELLOW}[1/6] Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed!${NC}"
    exit 1
fi
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker and Docker Compose found${NC}\n"

# Create directory structure
echo -e "${YELLOW}[2/6] Creating directory structure...${NC}"
mkdir -p central-platform/dashboards
mkdir -p mqtt-middleware/config
mkdir -p edge-gateway-cell
mkdir -p edge-gateway-datacenter
mkdir -p edge-gateway-switchroom
echo -e "${GREEN}✓ Directory structure created${NC}\n"

# Stop existing containers
echo -e "${YELLOW}[3/6] Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true
echo -e "${GREEN}✓ Existing containers stopped${NC}\n"

# Build images
echo -e "${YELLOW}[4/6] Building Docker images...${NC}"
echo "This may take several minutes on first run..."
docker-compose build --parallel
echo -e "${GREEN}✓ Docker images built successfully${NC}\n"

# Start services
echo -e "${YELLOW}[5/6] Starting services...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ All services started${NC}\n"

# Wait for services to be ready
echo -e "${YELLOW}[6/6] Waiting for services to be ready...${NC}"
echo "Waiting 30 seconds for initialization..."
for i in {30..1}; do
    echo -ne "\rTime remaining: ${i} seconds  "
    sleep 1
done
echo -e "\n${GREEN}✓ Services should be ready${NC}\n"

# Show status
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}\n"

echo "Container Status:"
docker-compose ps

echo -e "\n${BLUE}════════════════════════════════════════${NC}"
echo "Access Points:"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}Grafana Dashboard:${NC}     http://localhost:3000"
echo "                        (admin/admin)"
echo -e "${GREEN}Central Platform API:${NC}  http://localhost:8080/api"
echo -e "${GREEN}MQTT Broker:${NC}           mqtt://localhost:1883"
echo "                        (greengrid/greengrid123)"
echo -e "${GREEN}Cell Site API:${NC}         http://localhost:8081/api"
echo -e "${GREEN}Data Center API:${NC}       http://localhost:8082/api"
echo -e "${GREEN}Switch Room HMI:${NC}       http://localhost:8083"
echo -e "${BLUE}════════════════════════════════════════${NC}\n"

# Test connections
echo -e "${YELLOW}Testing services...${NC}"
sleep 5

echo -n "Central Platform: "
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Online${NC}"
else
    echo -e "${RED}✗ Offline${NC}"
fi

echo -n "Cell Site:        "
if curl -s http://localhost:8081/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Online${NC}"
else
    echo -e "${RED}✗ Offline${NC}"
fi

echo -n "Data Center:      "
if curl -s http://localhost:8082/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Online${NC}"
else
    echo -e "${RED}✗ Offline${NC}"
fi

echo -n "Switch Room:      "
if curl -s http://localhost:8083/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Online${NC}"
else
    echo -e "${RED}✗ Offline${NC}"
fi

echo -e "\n${BLUE}════════════════════════════════════════${NC}"
echo "Useful Commands:"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo "View logs:          docker-compose logs -f [service]"
echo "Stop all:           docker-compose down"
echo "Restart service:    docker-compose restart [service]"
echo "Monitor MQTT:       python3 monitor-mqtt.py"
echo "Run tests:          bash test-deployment.sh"
echo -e "${BLUE}════════════════════════════════════════${NC}\n"

echo -e "${GREEN}🎉 Greengrid Telco is now running!${NC}"
echo -e "Monitor real-time data at: ${BLUE}http://localhost:8083${NC} (Switch Room HMI)"
echo ""
