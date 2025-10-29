-- Initialize VirtPLC database schema
-- This script runs automatically on first PostgreSQL startup

CREATE EXTENSION
IF NOT EXISTS "uuid-ossp";

-- AI analysis logs
CREATE TABLE
IF NOT EXISTS ai_analysis_logs
(
    id SERIAL PRIMARY KEY,
    analysis_type VARCHAR
(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_used VARCHAR
(50),
    input_data_summary JSONB,
    output_summary JSONB,
    confidence_score FLOAT,
    execution_time_ms INTEGER,
    tokens_used INTEGER,
    error_message TEXT,
    success BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_ai_analysis_logs_timestamp ON ai_analysis_logs(timestamp);
CREATE INDEX idx_ai_analysis_logs_type ON ai_analysis_logs(analysis_type);

-- Metric definitions
CREATE TABLE
IF NOT EXISTS metric_definitions
(
    id SERIAL PRIMARY KEY,
    metric_key VARCHAR
(100) UNIQUE NOT NULL,
    display_name VARCHAR
(100) NOT NULL,
    description TEXT,
    unit VARCHAR
(20),
    category VARCHAR
(50),
    source_system VARCHAR
(50),
    timebase_field VARCHAR
(100),
    aggregation_methods JSONB,
    normal_range_min FLOAT,
    normal_range_max FLOAT,
    critical_threshold FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metric_definitions_key ON metric_definitions(metric_key);
CREATE INDEX idx_metric_definitions_category ON metric_definitions(category);

-- Insert sample metric definitions
INSERT INTO metric_definitions
    (metric_key, display_name, description, unit, category, source_system, timebase_field, aggregation_methods, normal_range_min, normal_range_max, critical_threshold)
VALUES
    ('motor1_temperature', 'Motor 1 Temperature', 'Motor 1 bearing temperature', 'celsius', 'temperature', 'opc-ua', 'temperature', '["avg", "min", "max"]', 50, 75, 85),
    ('motor2_temperature', 'Motor 2 Temperature', 'Motor 2 bearing temperature', 'celsius', 'temperature', 'opc-ua', 'temperature', '["avg", "min", "max"]', 50, 75, 85),
    ('motor1_vibration', 'Motor 1 Vibration', 'Motor 1 vibration level', 'mm/s', 'vibration', 'opc-ua', 'vibration', '["avg", "max"]', 0, 3.5, 5.0),
    ('motor2_vibration', 'Motor 2 Vibration', 'Motor 2 vibration level', 'mm/s', 'vibration', 'opc-ua', 'vibration', '["avg", "max"]', 0, 3.5, 5.0),
    ('conveyor1_speed', 'Conveyor 1 Speed', 'Conveyor belt speed', 'm/min', 'speed', 'opc-ua', 'speed', '["avg"]', 0, 100, 120),
    ('sensor1_pressure', 'Sensor 1 Pressure', 'Hydraulic pressure sensor 1', 'bar', 'pressure', 'opc-ua', 'pressure', '["avg", "min", "max"]', 50, 150, 180)
ON CONFLICT
(metric_key) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO virtplc;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO virtplc;
