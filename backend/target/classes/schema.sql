-- Database schema for VirtPLC Backend
-- This script creates all necessary tables for the application

-- Drop existing tables if they exist (for development)
DROP TABLE IF EXISTS users
CASCADE;
DROP TABLE IF EXISTS companies
CASCADE;
DROP TABLE IF EXISTS sensor_data
CASCADE;

-- Companies table
CREATE TABLE companies
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
CREATE TABLE users
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
    company_id BIGINT NOT NULL REFERENCES companies(id)
);

-- Create indexes
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_company_id ON users (company_id);
CREATE INDEX idx_companies_domain ON companies (domain);

-- Initialize TimescaleDB hypertable for sensor data
-- This script creates the hypertable for time-series optimization

-- Create the regular table first
CREATE TABLE sensor_data
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
CREATE INDEX idx_sensor_data_device_timestamp ON sensor_data (device_id, timestamp DESC);
CREATE INDEX idx_sensor_data_timestamp ON sensor_data (timestamp DESC);