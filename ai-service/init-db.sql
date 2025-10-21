-- Initialize VirtPLC database schema
-- This script runs automatically on first PostgreSQL startup

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Chat sessions
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_created ON chat_sessions(created_at);
CREATE INDEX idx_chat_sessions_expires ON chat_sessions(expires_at);

-- Chat messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER,
    model_used VARCHAR(50),
    metadata JSONB
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_timestamp ON chat_messages(timestamp);

-- User dashboards
CREATE TABLE IF NOT EXISTS user_dashboards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dashboard_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_default BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_user_dashboards_user ON user_dashboards(user_id);

-- Dashboard components
CREATE TABLE IF NOT EXISTS dashboard_components (
    id SERIAL PRIMARY KEY,
    dashboard_id INTEGER NOT NULL REFERENCES user_dashboards(id) ON DELETE CASCADE,
    component_type VARCHAR(50) NOT NULL,
    component_name VARCHAR(100) NOT NULL,
    config JSONB NOT NULL,
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    width INTEGER DEFAULT 4,
    height INTEGER DEFAULT 3,
    prompt_text TEXT,
    ai_generated BOOLEAN DEFAULT FALSE,
    generation_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_dashboard_components_dashboard ON dashboard_components(dashboard_id);

-- AI analysis logs
CREATE TABLE IF NOT EXISTS ai_analysis_logs (
    id SERIAL PRIMARY KEY,
    analysis_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_used VARCHAR(50),
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
CREATE TABLE IF NOT EXISTS metric_definitions (
    id SERIAL PRIMARY KEY,
    metric_key VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    unit VARCHAR(20),
    category VARCHAR(50),
    source_system VARCHAR(50),
    timebase_field VARCHAR(100),
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
INSERT INTO metric_definitions (metric_key, display_name, description, unit, category, source_system, timebase_field, aggregation_methods, normal_range_min, normal_range_max, critical_threshold)
VALUES
    ('motor1_temperature', 'Motor 1 Temperature', 'Motor 1 bearing temperature', 'celsius', 'temperature', 'opc-ua', 'temperature', '["avg", "min", "max"]', 50, 75, 85),
    ('motor2_temperature', 'Motor 2 Temperature', 'Motor 2 bearing temperature', 'celsius', 'temperature', 'opc-ua', 'temperature', '["avg", "min", "max"]', 50, 75, 85),
    ('motor1_vibration', 'Motor 1 Vibration', 'Motor 1 vibration level', 'mm/s', 'vibration', 'opc-ua', 'vibration', '["avg", "max"]', 0, 3.5, 5.0),
    ('motor2_vibration', 'Motor 2 Vibration', 'Motor 2 vibration level', 'mm/s', 'vibration', 'opc-ua', 'vibration', '["avg", "max"]', 0, 3.5, 5.0),
    ('conveyor1_speed', 'Conveyor 1 Speed', 'Conveyor belt speed', 'm/min', 'speed', 'opc-ua', 'speed', '["avg"]', 0, 100, 120),
    ('sensor1_pressure', 'Sensor 1 Pressure', 'Hydraulic pressure sensor 1', 'bar', 'pressure', 'opc-ua', 'pressure', '["avg", "min", "max"]', 50, 150, 180)
ON CONFLICT (metric_key) DO NOTHING;

-- Insert demo user
INSERT INTO users (username, email, full_name, role)
VALUES ('demo', 'demo@virtplc.com', 'Demo User', 'admin')
ON CONFLICT (username) DO NOTHING;

-- Auto-cleanup function for old chat messages
CREATE OR REPLACE FUNCTION cleanup_old_chat_messages()
RETURNS void AS $$
BEGIN
    DELETE FROM chat_messages
    WHERE timestamp < NOW() - INTERVAL '30 days';
    
    DELETE FROM chat_sessions
    WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO virtplc;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO virtplc;
