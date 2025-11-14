-- Initialize TimescaleDB extension
CREATE EXTENSION
IF NOT EXISTS timescaledb;

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