# TimeBaseDB Configuration

## Database Setup

TimeBaseDB configuration for storing historical data from the VirtPLC system.

## Connection Settings

```yaml
# timebase.yaml
server:
  host: localhost
  port: 8011
  
security:
  enabled: false  # Enable for production
  
storage:
  location: /timebase/data
  cache:
    size: 512MB
    
streams:
  - name: factory_data
    key: SYMBOL
    periodicity: IRREGULAR
    highAvailability: false
    
  - name: motor_telemetry
    key: SYMBOL
    periodicity: IRREGULAR
    schema: motor_schema
    
  - name: alarms_events
    key: SYMBOL
    periodicity: IRREGULAR
    schema: alarm_schema
```

## Schema Definitions

### Motor Telemetry Schema

```xml
<?xml version="1.0" encoding="UTF-8"?>
<types>
  <class name="MotorData">
    <field name="equipmentId" type="VARCHAR(50)" />
    <field name="speed" type="FLOAT" />
    <field name="temperature" type="FLOAT" />
    <field name="running" type="BOOLEAN" />
    <field name="fault" type="BOOLEAN" />
    <field name="targetSpeed" type="FLOAT" />
  </class>
</types>
```

### Conveyor Telemetry Schema

```xml
<?xml version="1.0" encoding="UTF-8"?>
<types>
  <class name="ConveyorData">
    <field name="equipmentId" type="VARCHAR(50)" />
    <field name="speed" type="FLOAT" />
    <field name="running" type="BOOLEAN" />
    <field name="itemCount" type="INTEGER" />
  </class>
</types>
```

### Sensor Data Schema

```xml
<?xml version="1.0" encoding="UTF-8"?>
<types>
  <class name="SensorData">
    <field name="sensorId" type="VARCHAR(50)" />
    <field name="detected" type="BOOLEAN" />
    <field name="distance" type="FLOAT" />
    <field name="temperature" type="FLOAT" />
    <field name="humidity" type="FLOAT" />
  </class>
</types>
```

### Alarm Schema

```xml
<?xml version="1.0" encoding="UTF-8"?>
<types>
  <class name="AlarmEvent">
    <field name="alarmId" type="VARCHAR(100)" />
    <field name="severity" type="VARCHAR(20)" />
    <field name="equipment" type="VARCHAR(50)" />
    <field name="message" type="VARCHAR(255)" />
    <field name="acknowledged" type="BOOLEAN" />
    <field name="ackUser" type="VARCHAR(50)" />
  </class>
</types>
```

## Data Retention Policies

```sql
-- Motors and conveyor data (30 days)
ALTER STREAM motor_telemetry SET 
  RETENTION POLICY '30 DAYS';

-- Sensor data (7 days)  
ALTER STREAM sensor_data SET 
  RETENTION POLICY '7 DAYS';

-- Alarms (1 year)
ALTER STREAM alarms_events SET 
  RETENTION POLICY '365 DAYS';
```

## Ignition Historian Configuration

In Ignition Gateway Config:

1. **Database Connection**:
   - Driver: TimeBase JDBC
   - URL: `dts://localhost:8011`
   - Database: `factory_data`

2. **Historian Provider**:
   - Name: `TimeBase-Historian`
   - Storage Provider: TimeBaseDB
   - Partition: `factory_data`
   - Buffer Size: 10000 samples
   - Store and Forward: Enabled
   - Max Storage: 100MB

3. **Tag Groups**:
   - Fast (500ms): Motor speed, sensor proximity
   - Medium (1s): Temperature, conveyor status
   - Slow (5s): Humidity, ambient sensors
   - On Change: Status booleans, alarms

## Query Examples

### Get Motor Speed History

```sql
SELECT 
  timestamp,
  equipmentId,
  speed,
  temperature
FROM motor_telemetry
WHERE 
  equipmentId = 'Motor1'
  AND timestamp BETWEEN '2025-10-19T00:00:00Z' 
                   AND '2025-10-19T23:59:59Z'
ORDER BY timestamp DESC;
```

### Calculate Average Speed

```sql
SELECT 
  equipmentId,
  AVG(speed) as avg_speed,
  MAX(temperature) as max_temp
FROM motor_telemetry
WHERE 
  timestamp > NOW() - INTERVAL '1 HOUR'
GROUP BY equipmentId;
```

### Get Active Alarms

```sql
SELECT 
  alarmId,
  severity,
  equipment,
  message,
  timestamp
FROM alarms_events
WHERE 
  acknowledged = false
ORDER BY severity DESC, timestamp DESC;
```

## Docker Deployment

```yaml
version: '3.8'

services:
  timebase:
    image: deltixinc/timebase:latest
    container_name: virtplc-timebase
    ports:
      - "8011:8011"
      - "8055:8055"  # Admin UI
    volumes:
      - ./TimeBaseDB/config:/timebase/config
      - timebase-data:/timebase/data
    environment:
      - TB_LICENSE=free
      - TB_ADMIN_USER=admin
      - TB_ADMIN_PASSWORD=changeme
    restart: unless-stopped

volumes:
  timebase-data:
```

## Performance Tuning

### Cache Configuration

```properties
# timebase.properties
cache.size=512M
cache.warmup=true
cache.compression=lz4
```

### Write Performance

```properties
writer.buffer.size=10000
writer.flush.interval=1000
writer.compression=true
```

### Query Optimization

- Index timestamp fields
- Use appropriate time ranges
- Limit result sets
- Enable query caching

## Monitoring

### Check Stream Status

```bash
# Using TimeBase CLI
qql -c "SELECT * FROM listStreams()"
```

### View Storage Usage

```bash
# Check data directory size
du -sh /timebase/data/*
```

### Monitor Connections

Check Ignition logs:
```
/usr/local/ignition/logs/wrapper.log
```

Look for TimeBase connection status.

## Backup and Recovery

### Backup Script

```bash
#!/bin/bash
# backup-timebase.sh

BACKUP_DIR="/backups/timebase"
DATE=$(date +%Y%m%d_%H%M%S)

# Stop writes temporarily (optional)
# qql -c "ALTER STREAM factory_data SET READONLY"

# Backup data directory
tar -czf "$BACKUP_DIR/timebase_$DATE.tar.gz" /timebase/data

# Resume writes
# qql -c "ALTER STREAM factory_data SET READWRITE"

# Keep last 7 days
find "$BACKUP_DIR" -name "timebase_*.tar.gz" -mtime +7 -delete
```

### Restore

```bash
# Stop TimeBase
systemctl stop timebase

# Restore data
tar -xzf /backups/timebase/timebase_20251019.tar.gz -C /

# Start TimeBase
systemctl start timebase
```

## Troubleshooting

### Connection Issues

1. Check TimeBase service status
2. Verify port 8011 is open
3. Check JDBC driver in Ignition
4. Review connection string format

### Data Not Storing

1. Verify historian provider is enabled
2. Check tag history configuration
3. Review store-and-forward buffer
4. Check disk space on TimeBase server

### Performance Issues

1. Increase cache size
2. Optimize retention policies
3. Add indexes on query fields
4. Check network latency

## Integration with Ignition

The TimeBase historian automatically stores data for any tag with `historyEnabled = true`. Data is accessible via:

1. **Power Chart Component**: Real-time and historical trends
2. **Easy Chart**: Simple historical data display
3. **Reporting Module**: Scheduled reports with historical data
4. **Scripting**: `system.tag.queryTagHistory()` function

## Next Steps

1. Import schema definitions
2. Create streams
3. Configure retention policies
4. Test data ingestion
5. Validate query performance
6. Set up backups
