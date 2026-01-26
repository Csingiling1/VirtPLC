# Device Management System

The VirtPLC system now supports dynamic device configuration through a database-driven approach. This replaces the hardcoded device mappings with a flexible, extensible system that can handle any type of industrial device.

## Overview

The device management system consists of:

1. **Device Entity**: Represents any industrial device (motors, conveyors, sensors, etc.)
2. **Device Mapping**: Defines how device data maps to SensorData fields
3. **Generic Mapping Service**: Uses database configuration instead of hardcoded logic
4. **Management APIs**: REST endpoints for device configuration
5. **Data Freshness Checks**: Prevents showing stale data when sources are offline

## Key Features

### Dynamic Device Support
- Add any type of device without code changes
- Configure data mappings through database
- Support for numeric, boolean, and string data types
- Configurable scaling, offsets, and units

### Data Freshness Validation
- Each device has a configurable timeout period
- System status indicates data freshness
- Frontend shows warnings when data is stale
- Prevents display of outdated information

### REST API Endpoints

#### Device Management
```
GET    /api/devices           # List all devices
GET    /api/devices/active    # List active devices
GET    /api/devices/{id}      # Get device by ID
POST   /api/devices           # Create new device
PUT    /api/devices/{id}      # Update device
DELETE /api/devices/{id}      # Delete device
```

#### Device Mappings
```
GET    /api/devices/{deviceId}/mappings     # Get mappings for device
POST   /api/devices/{deviceId}/mappings     # Create device mapping
PUT    /api/devices/mappings/{mappingId}    # Update mapping
DELETE /api/devices/mappings/{mappingId}    # Delete mapping
GET    /api/devices/mappings/active         # Get all active mappings
```

## Database Schema

### Devices Table
```sql
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    device_name VARCHAR(255) NOT NULL,
    device_type VARCHAR(100) NOT NULL,
    manufacturer_id VARCHAR(255),
    factory_id VARCHAR(255),
    plc_id VARCHAR(255),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    data_timeout_seconds INTEGER DEFAULT 300,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

### Device Mappings Table
```sql
CREATE TABLE device_mappings (
    id SERIAL PRIMARY KEY,
    device_id BIGINT REFERENCES devices(id),
    field_name VARCHAR(255) NOT NULL,
    field_type VARCHAR(50) NOT NULL,
    value_path VARCHAR(500),
    status_path VARCHAR(500),
    unit VARCHAR(50),
    multiplier DECIMAL(10,4) DEFAULT 1.0,
    offset DECIMAL(10,4) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

## Setup Instructions

1. **Run Database Migrations**
   ```bash
   # Ensure the devices and device_mappings tables are created
   # Tables are created via JPA @Entity annotations
   ```

2. **Initialize Device Configuration**
   ```bash
   # Run the setup script
   ./scripts/setup-devices.sh

   # Or set environment variables and run
   DB_HOST=localhost DB_PORT=5432 DB_NAME=virtplc DB_USER=postgres DB_PASSWORD=password ./scripts/setup-devices.sh
   ```

3. **Start the Application**
   ```bash
   # Backend will automatically use the new GenericDeviceMappingService
   # Frontend will show data freshness status
   ```

## Adding New Devices

### Via API
```bash
# Create a new device
curl -X POST http://localhost:8080/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "sensor_temp_zone_1",
    "deviceName": "Zone 1 Temperature Sensor",
    "deviceType": "sensor",
    "manufacturerId": "manufacturer-1",
    "factoryId": "factory-1",
    "plcId": "PLC-NY-001",
    "description": "Temperature sensor for production zone 1",
    "dataTimeoutSeconds": 300
  }'

# Add data mapping
curl -X POST http://localhost:8080/api/devices/9/mappings \
  -H "Content-Type: application/json" \
  -d '{
    "fieldName": "zone1Temp",
    "fieldType": "numeric",
    "valuePath": "$.signal_config.value",
    "unit": "celsius",
    "multiplier": 1.0,
    "offset": 0.0
  }'
```

### Via Database
```sql
-- Insert device
INSERT INTO devices (device_id, device_name, device_type, manufacturer_id, factory_id, plc_id, description, data_timeout_seconds)
VALUES ('sensor_temp_zone_1', 'Zone 1 Temperature Sensor', 'sensor', 'manufacturer-1', 'factory-1', 'PLC-NY-001', 'Temperature sensor for production zone 1', 300);

-- Insert mapping
INSERT INTO device_mappings (device_id, field_name, field_type, value_path, unit, multiplier, offset)
VALUES (9, 'zone1Temp', 'numeric', '$.signal_config.value', 'celsius', 1.0, 0.0);
```

## Data Freshness Logic

The system now checks data freshness based on device-specific timeouts:

- **Fresh Data**: Data age < device timeout → Shows live data
- **Stale Data**: Data age > device timeout → Shows warning, reduced quality score
- **No Data**: No data available → Shows "No data available" message

Frontend indicators:
- 🟢 Quality ≥90%: Live data
- 🟡 Quality 50-89%: Some stale data
- 🔴 Quality 30-49%: Mostly stale data
- ⚪ Quality <30%: No fresh data

## Migration from Hardcoded System

The old `DataMappingServiceImpl` is kept for reference but marked as legacy. The new `GenericDeviceMappingService` provides:

1. **Extensibility**: Add devices without code changes
2. **Flexibility**: Support any data type and mapping logic
3. **Maintainability**: Configuration stored in database
4. **Performance**: Cached mappings with automatic refresh

## Benefits

1. **No Code Changes**: Add new devices through API/database
2. **Type Safety**: Strong typing for device configurations
3. **Scalability**: Handle hundreds of devices efficiently
4. **Reliability**: Data freshness checks prevent stale data display
5. **Maintainability**: Clear separation of concerns with JPA entities

## Troubleshooting

### No Data Shown
- Check if devices are configured: `GET /api/devices/active`
- Verify Unreal Engine is running and sending data
- Check data freshness timeouts

### Mapping Not Working
- Verify device mappings exist: `GET /api/devices/{id}/mappings`
- Check JSON paths in value_path/status_path
- Ensure field names match SensorData properties

### Performance Issues
- Mappings are cached; restart service if cache issues occur
- Check database indexes on device_id columns
- Monitor query performance with slow query logs