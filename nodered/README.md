# Node-RED Data Pipeline

Node-RED flows for MQTT data enrichment and routing in VirtPLC.

## Overview

Node-RED acts as the central data enrichment pipeline, processing raw MQTT messages from PLCs and simulators, adding metadata, validation, and routing to appropriate services.

## Architecture

```
PLC/Simulator (MQTT)
    ↓
Node-RED (Enrichment & Validation)
    ↓
├─→ Collector (TimescaleDB)
├─→ Backend (Real-time Updates)
└─→ AI Service (Analytics)
```

## Flows

### Main Flows

1. **Hybrid: Sim + Unreal + Real** (`flow.json`)
   - Merges data from legacy simulator, Unreal Engine, and real PLCs
   - Validates and enriches incoming data
   - Routes to appropriate downstream services

2. **MQTT to Collector Pipeline**
   - Subscribes to PLC topics
   - Adds timestamps and metadata
   - Publishes to `factory/processed` topic

3. **Modbus Sync**
   - Synchronizes with Virtual PLC Modbus server
   - Enables Ignition HMI integration

## Configuration

### Environment Variables

```bash
MQTT_BROKER=mqtt
MQTT_PORT=1883
NODE_RED_USERNAME=admin
NODE_RED_PASSWORD_HASH=<bcrypt-hash>
```

### Settings

Configuration is managed through `settings.js`:

- **Flow File**: Flows stored in `flows/flows.json`
- **User Directory**: `/data`
- **Port**: 1880 (default)
- **Security**: Disabled by default for development

## Flow Structure

```javascript
// Global Context Variables
mqtt_broker: process.env.MQTT_BROKER || 'mqtt'
mqtt_port: process.env.MQTT_PORT || 1883
```

## Key Nodes

### MQTT Input Nodes
- **plc/+**: Legacy simulator data
- **factory/data/#**: Unreal Engine data
- **device/+/telemetry**: Real device data

### Function Nodes
- **Data Validator**: Validates incoming JSON schema
- **Metadata Enricher**: Adds timestamp, source, quality metrics
- **Data Router**: Routes to appropriate downstream services

### Output Nodes
- **factory/processed**: Enriched data for Collector
- **factory/alerts**: Critical alerts for monitoring
- **factory/raw**: Raw data archive

## Development

### Accessing Node-RED UI

```bash
# Local development
http://localhost:1880

# Docker deployment
docker-compose up nodered
```

### Editing Flows

1. Access Node-RED UI at http://localhost:1880
2. Import/export flows from the UI
3. Flows are persisted to `flows/flows.json`
4. Commit flow changes to version control

### Testing Flows

Use the **debug** node to monitor message flow:

```javascript
// Debug node outputs to Node-RED debug panel
msg.payload
msg.topic
msg._msgid
```

## MQTT Topics

### Input Topics

| Topic | Description | Source |
|-------|-------------|--------|
| `plc/+` | Legacy simulator data | Simulator |
| `factory/data/#` | Unreal Engine telemetry | Unreal Factory |
| `device/+/telemetry` | Real PLC data | Physical PLCs |

### Output Topics

| Topic | Description | Consumers |
|-------|-------------|-----------|
| `factory/processed` | Enriched data | Collector |
| `factory/alerts` | Critical alerts | Monitoring |
| `factory/raw` | Raw data backup | Archive |

## Data Schema

### Input Schema (Raw)
```json
{
  "device_id": "plc-001",
  "temperature": 25.5,
  "pressure": 101.3
}
```

### Output Schema (Enriched)
```json
{
  "device_id": "plc-001",
  "type": "sensor",
  "timestamp": 1234567890.123,
  "data": {
    "temperature": 25.5,
    "pressure": 101.3
  },
  "metadata": {
    "source": "plc",
    "node_red_version": "3.0",
    "processed_at": "2024-01-01T00:00:00Z"
  },
  "data_quality": {
    "validation": "passed",
    "completeness": 1.0
  },
  "category": "environmental",
  "priority": "normal"
}
```

## Backup and Restore

### Export Flows
```bash
# Backup current flows
cp flows/flows.json flows/flows.backup.json
```

### Import Flows
1. Access Node-RED UI
2. Menu → Import → Clipboard
3. Paste flow JSON and deploy

## Performance

- **Throughput**: ~5,000 messages/second
- **Latency**: <5ms processing time
- **Memory**: ~100MB baseline usage

## Troubleshooting

### Node-RED won't start
- Check port 1880 is not in use: `lsof -i :1880`
- Verify flows file is valid JSON: `jq . flows/flows.json`
- Check logs: `docker-compose logs nodered`

### MQTT connection failed
- Verify MQTT broker is running
- Check MQTT_BROKER environment variable
- Test connection: `mosquitto_sub -h mqtt -t '#' -v`

### Data not flowing to Collector
- Check MQTT topic matches Collector subscription
- Verify enriched data schema is valid
- Check Node-RED debug panel for errors

## Related Services

- [Collector](../collector/README.md) - Data ingestion service
- [Backend](../backend/README.md) - REST API
- [Simulator](../simulator/README.md) - PLC simulator

## Additional Resources

- [Node-RED Documentation](https://nodered.org/docs/)
- [MQTT Protocol](https://mqtt.org/)
- [Flow Examples](./flows/)
