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
    system_status VARCHAR(255) DEFAULT 'Running',
    quality INTEGER DEFAULT 192
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sensor_data_device_timestamp ON sensor_data (device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data (timestamp DESC);