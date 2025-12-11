#!/bin/bash
# Test both simulator and Unreal Engine data flows

echo "=== Testing Complete Data Pipeline ==="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test 1: Simulator Data (plc/+ topic)
echo -e "${BLUE}Test 1: Publishing Simulator PLC Data${NC}"
docker exec virtplc-mqtt mosquitto_pub -h mqtt -u virtplc -P virtplc123 \
  -t "plc/motor1" \
  -m '{"device_id":"motor1","type":"plc","timestamp":'"$(date +%s)"',"data":{"name":"Motor Speed","signal_config":{"value":1500,"unit":"rpm"}},"metadata":{"factory":"TestFactory","tenant":"test"}}'

echo "✓ Published to plc/motor1"
echo ""

# Test 2: Simulator Sensor Data
echo -e "${BLUE}Test 2: Publishing Simulator Sensor Data${NC}"
docker exec virtplc-mqtt mosquitto_pub -h mqtt -u virtplc -P virtplc123 \
  -t "plc/temp_sensor" \
  -m '{"device_id":"temp_sensor","type":"sensor","timestamp":'"$(date +%s)"',"data":{"name":"Temperature","signal_config":{"value":72.5,"unit":"celsius"}},"metadata":{"factory":"TestFactory","tenant":"test"}}'

echo "✓ Published to plc/temp_sensor"
echo ""

# Test 3: Unreal Engine - Conveyor RPM
echo -e "${BLUE}Test 3: Publishing Unreal Conveyor1 RPM${NC}"
docker exec virtplc-mqtt mosquitto_pub -h mqtt -u virtplc -P virtplc123 \
  -t "unreal/factory/conveyor1/rpm" \
  -m '1500'

echo "✓ Published to unreal/factory/conveyor1/rpm"
echo ""

# Test 4: Unreal Engine - Conveyor2 RPM
echo -e "${BLUE}Test 4: Publishing Unreal Conveyor2 RPM${NC}"
docker exec virtplc-mqtt mosquitto_pub -h mqtt -u virtplc -P virtplc123 \
  -t "unreal/factory/conveyor2/rpm" \
  -m '1800'

echo "✓ Published to unreal/factory/conveyor2/rpm"
echo ""

# Test 5: Unreal Engine - Machine Position
echo -e "${BLUE}Test 5: Publishing Unreal Machine Position${NC}"
docker exec virtplc-mqtt mosquitto_pub -h mqtt -u virtplc -P virtplc123 \
  -t "unreal/factory/machine1/position" \
  -m '{"x":10.5,"y":20.3}'

echo "✓ Published to unreal/factory/machine1/position"
echo ""

# Test 6: Unreal Engine - Machine Status
echo -e "${BLUE}Test 6: Publishing Unreal Machine Status${NC}"
docker exec virtplc-mqtt mosquitto_pub -h mqtt -u virtplc -P virtplc123 \
  -t "unreal/factory/machine1/status" \
  -m '{"isReady":true,"isDone":false}'

echo "✓ Published to unreal/factory/machine1/status"
echo ""

# Wait for processing
echo "Waiting 2 seconds for data processing..."
sleep 2
echo ""

# Check Collector logs
echo -e "${BLUE}Checking Collector logs for data ingestion:${NC}"
docker logs virtplc-collector 2>&1 | grep -i "successfully processed" | tail -6
echo ""

# Check TimescaleDB for data
echo -e "${BLUE}Checking TimescaleDB for stored data:${NC}"
docker exec virtplc-timescale psql -U virtplc -d virtplc_ts -c "\
SELECT 
    timestamp,
    device_id,
    type,
    data->'name' as name,
    metadata->'source' as source
FROM plc_data 
ORDER BY timestamp DESC 
LIMIT 10;" 2>&1 | head -20

echo ""
echo -e "${GREEN}=== Pipeline Test Complete ===${NC}"
echo ""
echo "Expected data flow:"
echo "  1. Simulator (plc/+) → Node-RED → Collector → TimescaleDB"
echo "  2. Unreal (unreal/factory/#) → Node-RED → Ignition + Collector → TimescaleDB"
echo ""
echo "Check Node-RED UI at: http://localhost:1880"
echo "Check data in TimescaleDB: docker exec virtplc-timescale psql -U virtplc -d virtplc_ts"
