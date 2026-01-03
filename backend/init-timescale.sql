-- Initialize TimescaleDB extension
CREATE EXTENSION
IF NOT EXISTS timescaledb;

-- Create PLC data table
CREATE TABLE
IF NOT EXISTS plc_data
(
    timestamp TIMESTAMPTZ NOT NULL,
    device_id TEXT NOT NULL,
    type TEXT NOT NULL,
    data JSONB,
    metadata JSONB,
    rpm DOUBLE PRECISION,
    position_x DOUBLE PRECISION,
    position_y DOUBLE PRECISION,
    is_on BOOLEAN,
    in_operation BOOLEAN
);

-- Convert to hypertable
SELECT create_hypertable('plc_data', 'timestamp', if_not_exists
=> TRUE);

-- Create hypertables for time-series data
-- Convert sensor_data table to hypertable if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1
    FROM information_schema.tables
    WHERE table_name = 'sensor_data') THEN
        PERFORM create_hypertable
    ('sensor_data', 'timestamp', if_not_exists => TRUE);
END
IF;
END $$;