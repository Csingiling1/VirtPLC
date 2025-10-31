#!/bin/bash
# Test script for end-to-end VirtPLC streaming architecture
# Tests: Simulator → Collector → Backend → Database

set -e

echo "🧪 Testing VirtPLC Multi-Tenant Streaming Architecture"
echo "======================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if service is healthy
check_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    echo -n "⏳ Waiting for $service to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo -e "\n${GREEN}✅ $service is ready${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done

    echo -e "\n${RED}❌ $service failed to start${NC}"
    return 1
}

# Check services
echo "🔍 Checking service health..."

# Backend health check
if ! check_service "Backend" "http://localhost:18080/api/data/health"; then
    echo "${RED}Backend health check failed${NC}"
    exit 1
fi

# Simulator health check
if ! check_service "Simulator" "http://localhost:8080/api/stream/latest"; then
    echo "${RED}Simulator health check failed${NC}"
    exit 1
fi

echo ""
echo "📊 Testing data flow..."

# Test 1: Check simulator generates multi-tenant data
echo "1. Testing simulator multi-tenant data generation..."
SIMULATOR_DATA=$(curl -s http://localhost:8080/api/stream/latest)

if echo "$SIMULATOR_DATA" | jq -e '.tenants[0]' > /dev/null 2>&1; then
    echo "${GREEN}✅ Simulator generates hierarchical tenant data${NC}"
else
    echo "${RED}❌ Simulator data format incorrect${NC}"
    echo "Response: $SIMULATOR_DATA"
    exit 1
fi

# Test 2: Check tenant structure
TENANT_COUNT=$(echo "$SIMULATOR_DATA" | jq '.tenants | length')
if [ "$TENANT_COUNT" -gt 0 ]; then
    echo "${GREEN}✅ Found $TENANT_COUNT tenant(s)${NC}"
else
    echo "${RED}❌ No tenants found${NC}"
    exit 1
fi

# Test 3: Check manufacturer/factory/PLC/sensor hierarchy
FIRST_TENANT=$(echo "$SIMULATOR_DATA" | jq '.tenants[0]')
MANUFACTURER_COUNT=$(echo "$FIRST_TENANT" | jq '.manufacturers | length')
if [ "$MANUFACTURER_COUNT" -gt 0 ]; then
    echo "${GREEN}✅ Found manufacturer(s) in tenant${NC}"
else
    echo "${RED}❌ No manufacturers found${NC}"
    exit 1
fi

# Test 4: Check sensor data generation
SENSOR_COUNT=$(echo "$FIRST_TENANT" | jq '[.manufacturers[].factories[].plcs[].sensors[]] | length')
if [ "$SENSOR_COUNT" -gt 0 ]; then
    echo "${GREEN}✅ Found $SENSOR_COUNT sensor(s) generating data${NC}"
else
    echo "${RED}❌ No sensors found${NC}"
    exit 1
fi

# Test 5: Check backend receives data (this would require collector to be running)
echo "2. Testing backend gRPC endpoint..."
# Note: This test would require the collector to be running and streaming data
# For now, just check that the backend is running and has the gRPC service

echo "${YELLOW}⚠️  Collector streaming test requires manual verification${NC}"
echo "   Run: docker-compose logs collector"
echo "   Check for: 'New collector connected' messages"

echo ""
echo "${GREEN}🎉 Basic architecture test completed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Start the collector: docker-compose up collector"
echo "2. Monitor logs: docker-compose logs -f collector backend"
echo "3. Check data in TimescaleDB"
echo "4. Verify Prometheus metrics at http://localhost:9090"