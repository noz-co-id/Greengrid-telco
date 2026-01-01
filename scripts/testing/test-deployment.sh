#!/bin/bash
# test-deployment.sh
# Script untuk testing deployment lengkap

echo "======================================"
echo "Greengrid Telco - Deployment Test"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test functions
test_service() {
    local service_name=$1
    local url=$2
    
    echo -n "Testing ${service_name}... "
    response=$(curl -s -o /dev/null -w "%{http_code}" ${url})
    
    if [ $response -eq 200 ]; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED (HTTP ${response})${NC}"
        return 1
    fi
}

echo "1. Testing Central Platform..."
test_service "Health Check" "http://localhost:8080/health"
test_service "Sites API" "http://localhost:8080/api/sites"
test_service "Dashboard Summary" "http://localhost:8080/api/dashboard/summary"
echo ""

echo "2. Testing Edge Gateways..."
test_service "Cell Site" "http://localhost:8081/health"
test_service "Data Center" "http://localhost:8082/health"
test_service "Switch Room" "http://localhost:8083/health"
echo ""

echo "3. Checking MQTT Broker..."
docker exec greengrid-mqtt mosquitto_pub -h localhost -u greengrid -P greengrid123 -t "test/ping" -m "ping" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ MQTT Broker OK${NC}"
else
    echo -e "${RED}✗ MQTT Broker FAILED${NC}"
fi
echo ""

echo "4. Checking Container Status..."
docker-compose ps
echo ""

echo "5. Fetching Sample Data..."
echo "Cell Site Metrics:"
curl -s http://localhost:8081/api/metrics | jq '.metrics.energy_meter' | head -10
echo ""

echo "Data Center PUE:"
curl -s http://localhost:8082/api/pue | jq '.'
echo ""

echo "======================================"
echo "Test Complete!"
echo "======================================"
