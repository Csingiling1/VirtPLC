#!/bin/bash

# Device Configuration Setup Script
# This script initializes the device configuration for the VirtPLC system

echo "VirtPLC Device Configuration Setup"
echo "=================================="

# Database connection details
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-virtplc}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-password}

echo "Database Host: $DB_HOST"
echo "Database Port: $DB_PORT"
echo "Database Name: $DB_NAME"
echo "Database User: $DB_USER"
echo ""

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo "Error: psql command not found. Please install PostgreSQL client tools."
    exit 1
fi

# Export password for psql
export PGPASSWORD="$DB_PASSWORD"

echo "Checking database connection..."
if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" &> /dev/null; then
    echo "Error: Cannot connect to database. Please check your connection details."
    exit 1
fi

echo "Database connection successful."

# Check if tables exist
echo "Checking if device tables exist..."
TABLES_EXIST=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "
    SELECT COUNT(*) FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN ('devices', 'device_mappings');
" | tr -d ' ')

if [ "$TABLES_EXIST" -lt 2 ]; then
    echo "Error: Device tables do not exist. Please run database migrations first."
    echo "Make sure the following tables exist:"
    echo "  - devices"
    echo "  - device_mappings"
    exit 1
fi

echo "Device tables exist."

# Check if data already exists
echo "Checking if device data already exists..."
DATA_EXISTS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "
    SELECT COUNT(*) FROM devices;
" | tr -d ' ')

if [ "$DATA_EXISTS" -gt 0 ]; then
    echo "Device data already exists ($DATA_EXISTS devices found)."
    read -p "Do you want to clear existing data and reinitialize? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi

    echo "Clearing existing device data..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
        DELETE FROM device_mappings;
        DELETE FROM devices;
    "
fi

echo "Initializing device configuration..."

# Get the migration script path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_FILE="$SCRIPT_DIR/../backend/src/main/resources/db/migration/device_setup.sql"

if [ ! -f "$MIGRATION_FILE" ]; then
    echo "Error: Migration file not found: $MIGRATION_FILE"
    exit 1
fi

echo "Running migration script..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATION_FILE"

if [ $? -eq 0 ]; then
    echo "Device configuration initialized successfully!"

    # Show summary
    echo ""
    echo "Summary:"
    DEVICE_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM devices;" | tr -d ' ')
    MAPPING_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM device_mappings;" | tr -d ' ')

    echo "  - Devices created: $DEVICE_COUNT"
    echo "  - Mappings created: $MAPPING_COUNT"

    echo ""
    echo "You can now:"
    echo "1. Start the backend service"
    echo "2. Access device management APIs at /api/devices"
    echo "3. Add new devices dynamically through the API"
    echo ""
    echo "Example API calls:"
    echo "  GET /api/devices/active - List active devices"
    echo "  POST /api/devices - Create new device"
    echo "  GET /api/devices/{id}/mappings - Get device mappings"
else
    echo "Error: Failed to initialize device configuration."
    exit 1
fi