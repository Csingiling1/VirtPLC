# AI Service & Data Management Updates

## ✅ Completed Features

### 1. **Natural Language Queries for Factory Data**

The AI service now has direct access to TimescaleDB and can answer questions about factory data in natural language.

**Available API Endpoints:**

```bash
# Get database statistics
curl http://localhost:3001/api/factory/stats

# Search for devices
curl 'http://localhost:3001/api/factory/devices?search=motor&limit=10'

# Get device details
curl http://localhost:3001/api/factory/devices/PLC-NY-001?hours=24

# Get factory summary
curl http://localhost:3001/api/factory/factories

# Execute custom SQL query
curl -X POST http://localhost:3001/api/factory/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT device_id, COUNT(*) FROM plc_data GROUP BY device_id LIMIT 5"}'
```

**Example Queries the AI Can Answer:**
- "How many PLCs are currently active?"
- "Show me the motor temperature sensor data from the last hour"
- "Which factory has the most devices?"
- "What's the average value for motor_speed sensors?"
- "List all sensors in the acme-factory-ny"

**Technical Details:**
- **Service:** `virtplc-ai` (port 3001)
- **Database:** TimescaleDB `plc_data` table
- **Client:** Custom Python client (`src/services/timescale_client.py`)
- **Tools Available:**
  - `execute_query()` - Run custom SQL
  - `get_latest_readings()` - Recent device data
  - `get_device_stats()` - Device statistics
  - `get_factory_summary()` - Factory overview
  - `search_devices()` - Find devices by name/ID

### 2. **Automatic TimescaleDB Cleanup Cronjob**

A containerized cronjob automatically cleans up old data to prevent database bloat.

**Schedule:** Every 2 months (Jan, Mar, May, Jul, Sep, Nov) at 2 AM

**What it Does:**
1. Identifies the oldest 25% of data points in `plc_data`
2. Creates backup in `plc_data_archive` table
3. Deletes the oldest 25% of records
4. Runs VACUUM to reclaim disk space
5. Logs everything to `/var/log/timescale_cleanup.log`

**Manual Execution:**
```bash
# Run cleanup manually
docker exec virtplc-timescale-cleanup /app/scripts/timescale_cleanup.sh

# View cleanup logs
docker exec virtplc-timescale-cleanup cat /var/log/timescale_cleanup.log

# Check cron schedule
docker exec virtplc-timescale-cleanup crontab -l
```

**Statistics from Last Cleanup:**
- **Before:** 101,389 records
- **Deleted:** 25,334 records (25%)
- **After:** 76,090 records
- **Oldest Record:** Now starts from 2025-12-08 22:27:21 (was 2025-11-26)

**Service Details:**
- **Container:** `virtplc-timescale-cleanup`
- **Base Image:** postgres:16-alpine (for psql client)
- **Dependencies:** TimescaleDB
- **Script:** `/app/scripts/timescale_cleanup.sh`
- **Crontab:** `/etc/crontabs/root`

---

## Architecture Updates

### Data Flow for AI Queries

```
User Question
    ↓
AI Service (FastAPI)
    ↓
TimescaleDB Client (psycopg2)
    ↓
TimescaleDB (plc_data table)
    ↓
Results → AI Processing → Natural Language Answer
```

### Cleanup Service

```
Cron Scheduler (every 2 months)
    ↓
timescale_cleanup.sh
    ↓
1. Calculate 25% threshold
2. Backup to plc_data_archive
3. DELETE old records
4. VACUUM ANALYZE
    ↓
Logs to /var/log/timescale_cleanup.log
```

---

## Testing

### Test AI Factory Data Queries

```bash
# Check service is running
docker ps | grep virtplc-ai

# Test stats endpoint
curl http://localhost:3001/api/factory/stats | jq

# Search for motor sensors
curl 'http://localhost:3001/api/factory/devices?search=motor' | jq '.results[0:5]'

# Get factory summary
curl http://localhost:3001/api/factory/factories | jq
```

### Test Cleanup Cronjob

```bash
# Check cronjob is scheduled
docker exec virtplc-timescale-cleanup crontab -l

# Verify cron daemon is running
docker exec virtplc-timescale-cleanup ps aux | grep crond

# Run manual cleanup (test)
docker exec virtplc-timescale-cleanup /app/scripts/timescale_cleanup.sh

# View logs
docker exec virtplc-timescale-cleanup tail -f /var/log/timescale_cleanup.log
```

---

## Configuration

### AI Service Environment Variables

```env
TIMESCALE_HOST=timescale
TIMESCALE_PORT=5432
TIMESCALE_DB=virtplc_ts
TIMESCALE_USER=virtplc
TIMESCALE_PASSWORD=changeme
```

### Cleanup Service Environment Variables

```env
TIMESCALE_HOST=timescale
TIMESCALE_PORT=5432
TIMESCALE_DB=virtplc_ts
TIMESCALE_USER=virtplc
TIMESCALE_PASSWORD=changeme
```

### Adjust Cleanup Schedule

Edit `scripts/timescale_cleanup.cron`:
```cron
# Current: Every 2 months on 1st at 2 AM
0 2 1 1,3,5,7,9,11 * /app/scripts/timescale_cleanup.sh

# Monthly: 1st of every month at 2 AM
0 2 1 * * /app/scripts/timescale_cleanup.sh

# Weekly: Every Monday at 2 AM
0 2 * * 1 /app/scripts/timescale_cleanup.sh

# Daily: Every day at 2 AM
0 2 * * * /app/scripts/timescale_cleanup.sh
```

Then rebuild: `docker-compose build timescale-cleanup && docker-compose up -d timescale-cleanup`

---

## Troubleshooting

### AI Service Can't Connect to TimescaleDB

```bash
# Check connectivity
docker exec virtplc-ai nc -zv timescale 5432

# Test database connection
docker exec virtplc-ai python3 -c "
import psycopg2
conn = psycopg2.connect(host='timescale', port=5432, database='virtplc_ts', user='virtplc', password='changeme')
print('✅ Connected')
conn.close()
"

# Check AI service logs
docker logs virtplc-ai --tail 50
```

### Cleanup Job Not Running

```bash
# Check container is running
docker ps | grep cleanup

# Check cron daemon
docker exec virtplc-timescale-cleanup ps aux | grep crond

# Check logs for errors
docker logs virtplc-timescale-cleanup

# Restart service
docker-compose restart timescale-cleanup
```

### Data Not Being Cleaned

```bash
# Check cleanup logs
docker exec virtplc-timescale-cleanup cat /var/log/timescale_cleanup.log

# Check plc_data_archive for backed up data
docker exec virtplc-timescale psql -U virtplc -d virtplc_ts -c "SELECT COUNT(*) FROM plc_data_archive;"

# Manually trigger cleanup
docker exec virtplc-timescale-cleanup /app/scripts/timescale_cleanup.sh
```

---

## Next Steps

1. **Enhanced AI Queries**: Integrate Ollama for more sophisticated natural language understanding
2. **Predictive Analytics**: Use historical data for anomaly detection
3. **Custom Cleanup Policies**: Configure retention per device type or factory
4. **Data Compression**: Enable TimescaleDB compression for older chunks
5. **Alerts**: Send notifications when cleanup completes or fails
