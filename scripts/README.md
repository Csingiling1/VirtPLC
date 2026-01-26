# Scripts

Utility scripts for VirtPLC maintenance, deployment, and automation.

## Overview

This directory contains operational scripts for managing the VirtPLC platform, including database maintenance, device setup, and automated tasks.

## Scripts

### timescale_cleanup.sh

Automated TimescaleDB data retention and cleanup script.

**Purpose**: Remove old time-series data based on retention policies.

**Usage**:
```bash
./timescale_cleanup.sh [days]
```

**Parameters**:
- `days`: Number of days to retain data (default: 30)

**Features**:
- Removes data older than retention period
- Compresses recent data chunks
- Updates statistics
- Logs cleanup operations

**Scheduled Execution**:
```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * /path/to/timescale_cleanup.sh 30
```

### timescale_cleanup.cron

Cron configuration file for automated cleanup.

**Installation**:
```bash
# Install cron job
crontab timescale_cleanup.cron

# Verify installation
crontab -l
```

### setup-devices.sh

Initializes device configurations and metadata.

**Purpose**: Bootstrap device registry with initial configurations.

**Usage**:
```bash
./setup-devices.sh [config-file]
```

**Parameters**:
- `config-file`: Path to device configuration JSON (default: devices.json)

**Example Config** (`devices.json`):
```json
{
  "devices": [
    {
      "id": "plc-001",
      "name": "Production Line 1 PLC",
      "type": "plc",
      "manufacturer": "Siemens",
      "model": "S7-1200",
      "ip_address": "192.168.1.10",
      "tags": ["production", "line-1"]
    }
  ]
}
```

**Operations**:
1. Validates device configuration
2. Creates device entries in database
3. Configures tag mappings
4. Sets up monitoring rules

### Dockerfile.cleanup

Containerized cleanup utility for scheduled tasks.

**Purpose**: Run maintenance tasks in a containerized environment.

**Build**:
```bash
docker build -f Dockerfile.cleanup -t virtplc/cleanup:latest .
```

**Run**:
```bash
docker run -e TIMESCALE_HOST=timescale \
           -e RETENTION_DAYS=30 \
           virtplc/cleanup:latest
```

**Environment Variables**:
- `TIMESCALE_HOST`: TimescaleDB hostname
- `TIMESCALE_PORT`: TimescaleDB port (default: 5432)
- `TIMESCALE_USER`: Database username
- `TIMESCALE_PASSWORD`: Database password
- `TIMESCALE_DB`: Database name
- `RETENTION_DAYS`: Data retention period in days

## Common Tasks

### Database Maintenance

```bash
# Clean up old data (keep last 30 days)
./timescale_cleanup.sh 30

# Vacuum and analyze database
docker exec timescale psql -U virtplc -d virtplc_ts -c "VACUUM ANALYZE;"

# Check database size
docker exec timescale psql -U virtplc -d virtplc_ts -c "SELECT pg_size_pretty(pg_database_size('virtplc_ts'));"
```

### Device Management

```bash
# Initialize devices from config
./setup-devices.sh devices.json

# List all devices
curl http://localhost:8080/api/devices

# Add a single device
curl -X POST http://localhost:8080/api/devices \
  -H "Content-Type: application/json" \
  -d '{"id":"plc-002","name":"Line 2","type":"plc"}'
```

### Automated Cleanup

```bash
# Schedule daily cleanup at 2 AM
crontab -e

# Add this line:
0 2 * * * cd /path/to/scripts && ./timescale_cleanup.sh 30 >> /var/log/cleanup.log 2>&1
```

## Best Practices

1. **Backup Before Cleanup**: Always backup data before running cleanup scripts
2. **Test in Staging**: Test scripts in staging environment first
3. **Monitor Logs**: Check logs after running maintenance scripts
4. **Schedule Off-Peak**: Run maintenance during low-traffic periods
5. **Version Control**: Keep scripts in version control

## Troubleshooting

### Cleanup Script Fails

**Issue**: Script cannot connect to database

**Solution**:
```bash
# Check database connectivity
docker exec timescale pg_isready

# Verify credentials
echo $TIMESCALE_PASSWORD

# Check script permissions
chmod +x timescale_cleanup.sh
```

### Device Setup Fails

**Issue**: Cannot create devices

**Solution**:
```bash
# Validate JSON config
jq . devices.json

# Check backend API is running
curl http://localhost:8080/health

# Verify database schema
docker exec timescale psql -U virtplc -c "\dt"
```

### Cron Job Not Running

**Issue**: Scheduled tasks not executing

**Solution**:
```bash
# Check cron service
sudo service cron status

# Verify crontab entries
crontab -l

# Check cron logs
grep CRON /var/log/syslog

# Test script manually
bash -x ./timescale_cleanup.sh
```

## Development

### Adding New Scripts

1. Create script file with `.sh` extension
2. Add shebang: `#!/bin/bash`
3. Make executable: `chmod +x script.sh`
4. Document usage in this README
5. Add error handling and logging

### Script Template

```bash
#!/bin/bash
set -e  # Exit on error

# Script: my-script.sh
# Purpose: Description of what this script does
# Usage: ./my-script.sh [options]

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/var/log/my-script.log"

# Functions
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Main logic
log "Starting script..."
# Your code here
log "Script completed successfully"
```

## Related Documentation

- [Database Maintenance Guide](../docs/database-maintenance.md)
- [Deployment Guide](../docs/deployment/)
- [DevOps Best Practices](../docs/devops-guide.md)

## Additional Resources

- [Cron Syntax Guide](https://crontab.guru/)
- [Bash Scripting Guide](https://www.gnu.org/software/bash/manual/)
- [TimescaleDB Maintenance](https://docs.timescale.com/timescaledb/latest/how-to-guides/data-retention/)
