-- Database schema for VirtPLC Backend
-- This script creates all necessary tables for the application if they don't exist

-- Companies table
CREATE TABLE IF NOT EXISTS companies
(
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    domain VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    logo_url VARCHAR(500),
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Users table
CREATE TABLE IF NOT EXISTS users
(
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    company_id BIGINT REFERENCES companies(id)
);

-- Tenants table
CREATE TABLE IF NOT EXISTS tenants
(
    id BIGSERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Manufacturers table
CREATE TABLE IF NOT EXISTS manufacturers
(
    id BIGSERIAL PRIMARY KEY,
    manufacturer_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id)
);

-- Factories table
CREATE TABLE IF NOT EXISTS factories
(
    id BIGSERIAL PRIMARY KEY,
    factory_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    manufacturer_id BIGINT NOT NULL REFERENCES manufacturers(id),
    shape VARCHAR(50) DEFAULT 'rectangle',
    width INTEGER DEFAULT 100,
    height INTEGER DEFAULT 80,
    width_meters DOUBLE PRECISION DEFAULT 50.0,
    height_meters DOUBLE PRECISION DEFAULT 40.0,
    wireframe_color VARCHAR(20) DEFAULT '#3b82f6'
);

-- PLCs table
CREATE TABLE IF NOT EXISTS plcs
(
    id BIGSERIAL PRIMARY KEY,
    plc_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    factory_id BIGINT NOT NULL REFERENCES factories(id),
    x_position DOUBLE PRECISION DEFAULT 0.0,
    y_position DOUBLE PRECISION DEFAULT 0.0,
    width DOUBLE PRECISION DEFAULT 2.0,
    height DOUBLE PRECISION DEFAULT 1.5
);

-- Sensors table
CREATE TABLE IF NOT EXISTS sensors
(
    id BIGSERIAL PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    plc_id BIGINT NOT NULL REFERENCES plcs(id),
    -- Embedded SignalConfig fields
    signal_name VARCHAR(255) NOT NULL,
    signal_unit VARCHAR(50) NOT NULL,
    signal_value DOUBLE PRECISION,
    signal_generator VARCHAR(50),
    signal_is_running BOOLEAN,
    signal_min_value DOUBLE PRECISION,
    signal_max_value DOUBLE PRECISION,
    signal_mean DOUBLE PRECISION,
    signal_std_dev DOUBLE PRECISION,
    signal_rate DOUBLE PRECISION,
    signal_frequency DOUBLE PRECISION,
    signal_amplitude DOUBLE PRECISION,
    "signal_offset" DOUBLE PRECISION,
    signal_step_size DOUBLE PRECISION,
    signal_last_update DOUBLE PRECISION
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_company_id ON users (company_id);
CREATE INDEX IF NOT EXISTS idx_companies_domain ON companies (domain);
CREATE INDEX IF NOT EXISTS idx_tenants_tenant_id ON tenants (tenant_id);
CREATE INDEX IF NOT EXISTS idx_manufacturers_manufacturer_id ON manufacturers (manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_manufacturers_tenant_id ON manufacturers (tenant_id);
CREATE INDEX IF NOT EXISTS idx_factories_factory_id ON factories (factory_id);
CREATE INDEX IF NOT EXISTS idx_factories_manufacturer_id ON factories (manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_plcs_plc_id ON plcs (plc_id);
CREATE INDEX IF NOT EXISTS idx_plcs_factory_id ON plcs (factory_id);
CREATE INDEX IF NOT EXISTS idx_sensors_sensor_id ON sensors (sensor_id);
CREATE INDEX IF NOT EXISTS idx_sensors_plc_id ON sensors (plc_id);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_company_id ON users (company_id);
CREATE INDEX IF NOT EXISTS idx_companies_domain ON companies (domain);

-- Initialize TimescaleDB hypertable for sensor data
-- This script creates the hypertable for time-series optimization

-- Create the regular table first
CREATE TABLE IF NOT EXISTS sensor_data
(
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