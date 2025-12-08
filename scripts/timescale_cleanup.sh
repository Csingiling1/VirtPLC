#!/bin/bash
# TimescaleDB Data Cleanup Script
# Runs every 2 months to delete 25% of oldest and least-used data points

set -e

# Database connection parameters
DB_HOST="${TIMESCALE_HOST:-timescale}"
DB_PORT="${TIMESCALE_PORT:-5432}"
DB_NAME="${TIMESCALE_DB:-virtplc_ts}"
DB_USER="${TIMESCALE_USER:-virtplc}"
DB_PASSWORD="${TIMESCALE_PASSWORD:-changeme}"

# Logging
LOG_FILE="/var/log/timescale_cleanup.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

log "=== Starting TimescaleDB Cleanup ==="

# Function to execute SQL
execute_sql() {
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "$1"
}

# Get current statistics
log "Getting current database statistics..."
CURRENT_STATS=$(execute_sql "
    SELECT 
        COUNT(*) as total_records,
        pg_size_pretty(pg_total_relation_size('plc_data')) as table_size,
        MIN(timestamp) as oldest_record,
        MAX(timestamp) as newest_record
    FROM plc_data;
")
log "Current stats: $CURRENT_STATS"

# Calculate 25% threshold - target oldest 25% of data
log "Calculating 25% threshold timestamp..."
THRESHOLD_TIMESTAMP=$(execute_sql "
    WITH ranked AS (
        SELECT timestamp, 
               ROW_NUMBER() OVER (ORDER BY timestamp) as rn,
               COUNT(*) OVER () as total
        FROM plc_data
    )
    SELECT timestamp 
    FROM ranked 
    WHERE rn = CAST(total * 0.25 AS INTEGER)
    LIMIT 1;
")

if [ -z "$THRESHOLD_TIMESTAMP" ]; then
    log "ERROR: Could not calculate threshold timestamp"
    exit 1
fi

log "Threshold timestamp (25% mark): $THRESHOLD_TIMESTAMP"

# Get count of records to be deleted
DELETE_COUNT=$(execute_sql "
    SELECT COUNT(*) 
    FROM plc_data 
    WHERE timestamp < '$THRESHOLD_TIMESTAMP'::timestamptz;
")
log "Records to be deleted: $DELETE_COUNT"

# Create backup of data being deleted (optional - comment out if not needed)
log "Creating backup of data to be deleted..."
execute_sql "
    CREATE TABLE IF NOT EXISTS plc_data_archive (
        LIKE plc_data INCLUDING ALL
    );
    
    INSERT INTO plc_data_archive 
    SELECT * FROM plc_data 
    WHERE timestamp < '$THRESHOLD_TIMESTAMP'::timestamptz
    ON CONFLICT DO NOTHING;
"
log "Backup created in plc_data_archive table"

# Delete old data
log "Deleting oldest 25% of data..."
execute_sql "
    DELETE FROM plc_data 
    WHERE timestamp < '$THRESHOLD_TIMESTAMP'::timestamptz;
"
log "Deletion complete"

# Run VACUUM to reclaim space
log "Running VACUUM ANALYZE to reclaim space..."
execute_sql "VACUUM ANALYZE plc_data;"
log "VACUUM complete"

# Get new statistics
log "Getting updated database statistics..."
NEW_STATS=$(execute_sql "
    SELECT 
        COUNT(*) as total_records,
        pg_size_pretty(pg_total_relation_size('plc_data')) as table_size,
        MIN(timestamp) as oldest_record,
        MAX(timestamp) as newest_record
    FROM plc_data;
")
log "New stats: $NEW_STATS"

# Optionally compress older chunks (if using TimescaleDB compression)
log "Compressing old chunks (if compression is enabled)..."
execute_sql "
    SELECT compress_chunk(chunk)
    FROM show_chunks('plc_data', older_than => INTERVAL '30 days')
    AS chunk;
" || log "Compression skipped (may not be configured)"

log "=== Cleanup Complete ==="
log "Deleted $DELETE_COUNT records (25% of total)"
log "Next cleanup scheduled in 2 months"
