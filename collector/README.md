# Collector Service

Go-based MQTT to TimescaleDB data collector for VirtPLC.

## Overview

The Collector service subscribes to MQTT topics and persists incoming device data to TimescaleDB. It provides high-performance data ingestion with automatic batching and error handling.

## Features

- **MQTT Subscription**: Subscribes to enriched data from Node-RED
- **TimescaleDB Integration**: Efficient time-series data storage
- **Batch Processing**: Automatic batching for optimal database performance
- **Error Handling**: Robust error handling with retry logic
- **Schema Validation**: Validates incoming data against expected schema

## Architecture

```
MQTT Broker (factory/processed)
    ↓
Collector Service
    ↓
TimescaleDB (virtplc_ts.device_data)
```

## Configuration

Environment variables:

```bash
# Database Configuration
TIMESCALE_HOST=timescale
TIMESCALE_PORT=5432
TIMESCALE_USER=virtplc
TIMESCALE_PASSWORD=changeme
TIMESCALE_DB=virtplc_ts

# MQTT Configuration
MQTT_BROKER=mqtt
MQTT_PORT=1883
MQTT_TOPIC=factory/processed
```

## Data Schema

The collector expects JSON messages with the following structure:

```json
{
  "device_id": "device-001",
  "type": "sensor",
  "timestamp": 1234567890.123,
  "data": {
    "temperature": 25.5,
    "pressure": 101.3
  },
  "metadata": {
    "location": "factory-floor-1"
  },
  "category": "environmental",
  "priority": "normal"
}
```

## Building

```bash
# Local build
go build -o collector .

# Docker build
docker build -t virtplc/collector:latest .
```

## Running

```bash
# Run locally
./collector

# Run with Docker
docker run -e TIMESCALE_HOST=localhost virtplc/collector:latest
```

## Development

```bash
# Install dependencies
go mod download

# Run tests
go test ./...

# Format code
go fmt ./...
```

## Database Schema

The collector writes to the `device_data` table in TimescaleDB:

```sql
CREATE TABLE IF NOT EXISTS device_data (
    time TIMESTAMPTZ NOT NULL,
    device_id TEXT NOT NULL,
    type TEXT,
    data JSONB,
    metadata JSONB,
    category TEXT,
    priority TEXT
);

SELECT create_hypertable('device_data', 'time', if_not_exists => TRUE);
```

## Performance

- **Throughput**: ~10,000 messages/second
- **Latency**: <10ms average insert time
- **Batch Size**: Configurable (default: 100 messages)

## Monitoring

Key metrics to monitor:
- MQTT connection status
- Database connection pool utilization
- Insert throughput and latency
- Error rates

## Troubleshooting

### Cannot connect to MQTT broker
- Verify MQTT_BROKER and MQTT_PORT environment variables
- Check network connectivity: `telnet mqtt 1883`
- Verify MQTT broker is running

### Cannot connect to TimescaleDB
- Verify database credentials
- Check TimescaleDB is running: `docker ps | grep timescale`
- Verify database schema is initialized

### Data not appearing in database
- Check MQTT topic subscription matches Node-RED output
- Verify JSON schema matches expected format
- Check collector logs for parsing errors

## Related Services

- [Node-RED](../nodered/README.md) - Data enrichment pipeline
- [Backend](../backend/README.md) - REST API service
- [AI Service](../ai-service/README.md) - Analytics service
