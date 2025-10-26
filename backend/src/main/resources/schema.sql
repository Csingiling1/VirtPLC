-- Initialize TimescaleDB hypertable for sensor data
-- This script creates the hypertable for time-series optimization

-- Create the regular table first
CREATE TABLE IF NOT EXISTS sensor_data (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    device_id VARCHAR(255) NOT NULL,
    motor1_speed DOUBLE PRECISION,
    motor1_temp DOUBLE PRECISION,
    motor1_run BOOLEAN DEFAULT true,
    motor1_fault BOOLEAN DEFAULT false,
    motor2_speed DOUBLE PRECISION,
    motor2_temp DOUBLE PRECISION,
    motor2_run BOOLEAN DEFAULT true,
    motor2_fault BOOLEAN DEFAULT false,
    conveyor1_speed DOUBLE PRECISION,
    conveyor1_run BOOLEAN DEFAULT true,
    sensor1_value DOUBLE PRECISION,
    sensor2_value BOOLEAN,
    system_status VARCHAR(255) DEFAULT 'Running'
);

-- Convert to hypertable if TimescaleDB extension is available
-- This will create time-based partitions for better performance
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        PERFORM create_hypertable('sensor_data', 'timestamp', if_not_exists => TRUE);
    END IF;
END $$;

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sensor_data_device_timestamp ON sensor_data (device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data (timestamp DESC);

-- Create continuous aggregates for real-time analytics (if TimescaleDB is available)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        -- Create a continuous aggregate for hourly averages
        CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_data_hourly
        WITH (timescaledb.continuous) AS
        SELECT
            time_bucket('1 hour', timestamp) AS bucket,
            device_id,
            AVG(motor1_speed) AS avg_motor1_speed,
            AVG(motor1_temp) AS avg_motor1_temp,
            AVG(motor2_speed) AS avg_motor2_speed,
            AVG(motor2_temp) AS avg_motor2_temp,
            AVG(conveyor1_speed) AS avg_conveyor1_speed,
            AVG(sensor1_value) AS avg_sensor1_value,
            COUNT(*) AS sample_count
        FROM sensor_data
        GROUP BY bucket, device_id
        WITH NO DATA;

        -- Enable automatic refresh for the continuous aggregate
        SELECT add_continuous_aggregate_policy('sensor_data_hourly',
            start_offset => INTERVAL '3 hours',
            end_offset => INTERVAL '1 hour',
            schedule_interval => INTERVAL '1 hour');
    END IF;
END $$;