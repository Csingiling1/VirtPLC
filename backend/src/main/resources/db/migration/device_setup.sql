-- Database migration script for device configuration
-- Run this after creating the devices and device_mappings tables

-- Insert sample devices
INSERT INTO devices
    (device_id, device_name, device_type, manufacturer_id, factory_id, plc_id, description, is_active, data_timeout_seconds, created_at, updated_at)
VALUES
    ('motor_speed_PLC-NY-001', 'Motor 1 Speed', 'motor', 'manufacturer-1', 'factory-1', 'PLC-NY-001', 'Motor 1 speed sensor', true, 300, NOW(), NOW()),
    ('motor_temp_PLC-NY-001', 'Motor 1 Temperature', 'motor', 'manufacturer-1', 'factory-1', 'PLC-NY-001', 'Motor 1 temperature sensor', true, 300, NOW(), NOW()),
    ('motor_speed_PLC-NY-002', 'Motor 2 Speed', 'motor', 'manufacturer-1', 'factory-1', 'PLC-NY-002', 'Motor 2 speed sensor', true, 300, NOW(), NOW()),
    ('motor_temp_PLC-NY-002', 'Motor 2 Temperature', 'motor', 'manufacturer-1', 'factory-1', 'PLC-NY-002', 'Motor 2 temperature sensor', true, 300, NOW(), NOW()),
    ('Conveyor1_rpm', 'Conveyor 1 RPM', 'conveyor', 'manufacturer-1', 'factory-1', 'PLC-NY-001', 'Conveyor 1 speed sensor', true, 300, NOW(), NOW()),
    ('Conveyor1_status', 'Conveyor 1 Status', 'conveyor', 'manufacturer-1', 'factory-1', 'PLC-NY-001', 'Conveyor 1 status sensor', true, 300, NOW(), NOW()),
    ('Placer1_position', 'Placer 1 Position', 'placer', 'manufacturer-1', 'factory-1', 'PLC-NY-001', 'Placer 1 position sensor', true, 300, NOW(), NOW()),
    ('Placer1_status', 'Placer 1 Status', 'placer', 'manufacturer-1', 'factory-1', 'PLC-NY-001', 'Placer 1 status sensor', true, 300, NOW(), NOW());

-- Insert device mappings
INSERT INTO device_mappings
    (device_id, field_name, field_type, value_path, status_path, unit, multiplier, offset, is_active, created_at, updated_at)
VALUES
    -- Motor 1 mappings
    (1, 'motor1Speed', 'numeric', '$.signal_config.value', NULL, 'rpm', 1.0, 0.0, true, NOW(), NOW()),
    (2, 'motor1Temp', 'numeric', '$.signal_config.value', NULL, 'celsius', 1.0, 0.0, true, NOW(), NOW()),

    -- Motor 2 mappings
    (3, 'motor2Speed', 'numeric', '$.signal_config.value', NULL, 'rpm', 1.0, 0.0, true, NOW(), NOW()),
    (4, 'motor2Temp', 'numeric', '$.signal_config.value', NULL, 'celsius', 1.0, 0.0, true, NOW(), NOW()),

    -- Conveyor 1 mappings
    (5, 'conveyor1Rpm', 'numeric', '$.signal_config.value', NULL, 'rpm', 1.0, 0.0, true, NOW(), NOW()),
    (6, 'conveyor1Status', 'boolean', NULL, '$.signal_config.status', NULL, 1.0, 0.0, true, NOW(), NOW()),

    -- Placer 1 mappings
    (7, 'placer1Position', 'numeric', '$.signal_config.value', NULL, 'mm', 1.0, 0.0, true, NOW(), NOW()),
    (8, 'placer1Status', 'boolean', NULL, '$.signal_config.status', NULL, 1.0, 0.0, true, NOW(), NOW());