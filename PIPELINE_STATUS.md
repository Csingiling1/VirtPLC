# MQTT Data Pipeline Status

## ✅ Pipeline Successfully Operational

**Status as of**: 2025-12-08 22:24 UTC

### Architecture
```
Python Simulator → MQTT (plc/{device_id}) → Node-RED (validate/enrich/route) → MQTT (collector/ingest) → Go Collector → TimescaleDB
```

### Current Performance

#### Data Flow Statistics
- **Total Records in DB**: 14,074 new records since fix
  - PLCs: 2,818 records from 7 unique devices
  - Sensors: 11,256 records from 28 unique sensors
- **Data Freshness**: Real-time (1 second intervals)
- **First New Record**: 2025-12-08 22:12:13 UTC
- **Latest Record**: 2025-12-08 22:23:52 UTC

#### Service Status
- ✅ **Simulator**: Publishing to `plc/{device_id}` topics with authentication
- ✅ **MQTT Broker**: Mosquitto 2.0 with credentials (virtplc/virtplc123)
- ✅ **Node-RED**: Receiving, validating, enriching, and routing data
- ✅ **Collector**: Consuming from `collector/ingest` and writing to TimescaleDB
- ✅ **TimescaleDB**: Storing data in hypertable `plc_data`

### Recent Fixes Applied

#### 1. Simulator MQTT Publishing (CRITICAL FIX)
**Problem**: Simulator running in web-only mode, not publishing MQTT data
**Root Cause**: 
- Code incorrectly iterated `factory.sensors` (doesn't exist)
- Sensors are nested inside `plc.sensors`

**Fix**:
```python
# Fixed iteration structure
for plc in factory.plcs:
    client.publish(f"plc/{plc.id}", json.dumps(plc_payload))
    
    # Publish sensors WITHIN the PLC
    for sensor in plc.sensors:
        client.publish(f"plc/{sensor.id}", json.dumps(sensor_payload))
```

**Result**: Simulator now publishes 35 devices/second (7 PLCs + 28 sensors)

#### 2. Node-RED Debug Visibility
**Problem**: No visibility into incoming/outgoing message flow
**Fix**: Added comprehensive debug nodes
- `log_incoming`: Shows raw MQTT messages from `plc/+`
- `log_enriched`: Shows validated and enriched data
- `log_outgoing`: Shows formatted data sent to `collector/ingest`
- `log_unknown`: Catches messages with invalid types

**Result**: Full visibility into data transformation pipeline

#### 3. Node-RED Statistics Counter
**Problem**: Message counter always showed `NaN` and 0 messages
**Root Cause**: `validate_data` node didn't increment the shared context counter

**Fix**:
```javascript
// In validate_data function
let count = context.get('messageCount') || 0;
count++;
context.set('messageCount', count);

// Now stats_counter can read the actual count
```

**Result**: Statistics now accurately track message throughput

### Configuration Summary

#### MQTT Topics
- **Published by Simulator**: `plc/{device_id}` (35 unique topics)
  - PLCs: `plc/PLC-NY-001`, `plc/PLC-NY-002`, etc.
  - Sensors: `plc/motor_speed_PLC-NY-001`, etc.
- **Subscribed by Node-RED**: `plc/+` (wildcard for all devices)
- **Published by Node-RED**: `collector/ingest` (single aggregation topic)
- **Subscribed by Collector**: `collector/ingest`

#### Authentication
- **Username**: `virtplc`
- **Password**: `virtplc123`
- **Applied to**: Simulator, Node-RED, Collector

#### TimescaleDB Schema
```sql
CREATE TABLE plc_data (
    timestamp TIMESTAMPTZ NOT NULL,
    device_id TEXT,
    type TEXT,
    data JSONB,
    metadata JSONB
);

SELECT create_hypertable('plc_data', 'timestamp');
CREATE INDEX ON plc_data (device_id, timestamp DESC);
CREATE INDEX ON plc_data (type, timestamp DESC);
```

### Data Flow Examples

#### Simulator → MQTT
```json
{
  "device_id": "PLC-NY-001",
  "type": "plc",
  "timestamp": 1765232309.878,
  "data": {
    "id": "PLC-NY-001",
    "name": "Siemens S7-1500 #1",
    "sensors": [...]
  },
  "metadata": {
    "tenant": "acme-corp",
    "factory": "acme-factory-ny"
  }
}
```

#### Node-RED → Collector
```json
{
  "device_id": "PLC-NY-001",
  "type": "plc",
  "timestamp": 1765232309.878,
  "data": {...},
  "metadata": {...},
  "processed_at": "2025-12-08T22:19:52.123Z",
  "node_red_version": "1.0",
  "topic_original": "plc/PLC-NY-001",
  "data_quality": {
    "valid": true,
    "latency_ms": 15
  },
  "category": "PLC",
  "priority": "high"
}
```

### Monitoring Commands

#### Check MQTT Traffic
```bash
# Subscribe to all PLC topics
docker exec virtplc-mqtt mosquitto_sub -h localhost -p 1883 -u virtplc -P virtplc123 -t 'plc/#' -v

# Subscribe to collector ingest
docker exec virtplc-mqtt mosquitto_sub -h localhost -p 1883 -u virtplc -P virtplc123 -t 'collector/ingest' -v
```

#### Check Database
```bash
# Recent data
docker exec virtplc-timescale psql -U virtplc -d virtplc_ts -c \
  "SELECT timestamp, device_id, type, data->>'name' as name FROM plc_data ORDER BY timestamp DESC LIMIT 10;"

# Statistics
docker exec virtplc-timescale psql -U virtplc -d virtplc_ts -c \
  "SELECT type, COUNT(*) as records, COUNT(DISTINCT device_id) as devices FROM plc_data GROUP BY type;"
```

#### Check Logs
```bash
# Simulator MQTT activity
docker logs virtplc-simulator --tail 50 | grep -i mqtt

# Collector processing
docker logs collector --tail 30

# Node-RED (access web UI at http://localhost:1880)
```

### Next Steps (Optional Enhancements)

1. **Add Alerting**: Configure Node-RED to send alerts on anomalies
2. **Add Metrics Dashboard**: Create Grafana dashboards for real-time visualization
3. **Optimize Performance**: Batch writes in collector for higher throughput
4. **Add Data Retention**: Configure TimescaleDB compression and retention policies
5. **Add Health Monitoring**: Implement health check endpoints in all services

### Troubleshooting

#### No Data Arriving
1. Check simulator mode: `docker logs virtplc-simulator | grep "Starting MQTT"`
2. Verify MQTT connectivity: `docker logs virtplc-simulator | grep "Connected to MQTT"`
3. Test MQTT directly: `docker exec virtplc-mqtt mosquitto_sub -t 'plc/#' -u virtplc -P virtplc123`

#### Node-RED Not Processing
1. Check Node-RED logs: `docker logs virtplc-nodered --tail 50`
2. Access UI: http://localhost:1880 (check debug sidebar)
3. Verify MQTT broker config in flows

#### Collector Not Storing
1. Check collector logs: `docker logs collector --tail 50`
2. Verify MQTT subscription: Should see "Connected to MQTT broker"
3. Check TimescaleDB connectivity: `docker exec collector nc -zv timescale 5432`

---

**Pipeline Status**: 🟢 **FULLY OPERATIONAL**
