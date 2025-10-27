package com.virtplc.service;

import com.virtplc.model.SensorData;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Map;

/**
 * Flexible data mapper that can convert simulator data to SensorData format.
 * Handles any device structure by mapping common patterns.
 */
@Slf4j
@Service
public class FlexibleDataMapper {

    /**
     * Map simulator data to SensorData format.
     * Uses flexible mapping to handle any device structure.
     */
    public SensorData mapToSensorData(Map<String, Object> simulatorData) {
        log.debug("Mapping simulator data to SensorData format");
        
        SensorData.SensorDataBuilder builder = SensorData.builder()
                .timestamp(System.currentTimeMillis())
                .systemStatus("Running");

        // Map motor data - look for common patterns
        builder.motor1Speed(extractDouble(simulatorData, "motor1Speed", "Motor1.Speed", "motor1_speed"))
               .motor1Temp(extractDouble(simulatorData, "motor1Temp", "Motor1.Temperature", "motor1_temp"))
               .motor1Run(extractBoolean(simulatorData, "motor1Run", "Motor1.Running", "motor1_run", true))
               .motor1Fault(extractBoolean(simulatorData, "motor1Fault", "Motor1.Fault", "motor1_fault", false));

        builder.motor2Speed(extractDouble(simulatorData, "motor2Speed", "Motor2.Speed", "motor2_speed"))
               .motor2Temp(extractDouble(simulatorData, "motor2Temp", "Motor2.Temperature", "motor2_temp"))
               .motor2Run(extractBoolean(simulatorData, "motor2Run", "Motor2.Running", "motor2_run", true))
               .motor2Fault(extractBoolean(simulatorData, "motor2Fault", "Motor2.Fault", "motor2_fault", false));

        // Map conveyor data
        builder.conveyor1Speed(extractDouble(simulatorData, "conveyor1Speed", "Conveyor1.Speed", "conveyor1_speed"))
               .conveyor1Run(extractBoolean(simulatorData, "conveyor1Run", "Conveyor1.Running", "conveyor1_run", true));

        // Map sensor data
        builder.sensor1Value(extractDouble(simulatorData, "sensor1Value", "Sensor1.Value", "sensor1_value"))
               .sensor2Value(extractBoolean(simulatorData, "sensor2Value", "Sensor2.Value", "sensor2_value", false));

        // Try to extract system status
        String systemStatus = extractString(simulatorData, "systemStatus", "SystemStatus", "system_status");
        if (systemStatus != null) {
            builder.systemStatus(systemStatus);
        }

        return builder.build();
    }

    /**
     * Extract double value from data map using multiple possible keys.
     */
    private Double extractDouble(Map<String, Object> data, String... keys) {
        for (String key : keys) {
            Object value = data.get(key);
            if (value != null) {
                try {
                    if (value instanceof Number) {
                        return ((Number) value).doubleValue();
                    } else if (value instanceof String) {
                        return Double.parseDouble((String) value);
                    }
                } catch (NumberFormatException e) {
                    log.debug("Failed to parse double value for key {}: {}", key, value);
                }
            }
        }
        return 0.0;
    }

    /**
     * Extract boolean value from data map using multiple possible keys.
     */
    private Boolean extractBoolean(Map<String, Object> data, String... keys) {
        return extractBoolean(data, false, keys);
    }

    /**
     * Extract boolean value from data map using multiple possible keys with default.
     */
    private Boolean extractBoolean(Map<String, Object> data, Boolean defaultValue, String... keys) {
        for (String key : keys) {
            Object value = data.get(key);
            if (value != null) {
                if (value instanceof Boolean) {
                    return (Boolean) value;
                } else if (value instanceof String) {
                    return Boolean.parseBoolean((String) value);
                } else if (value instanceof Number) {
                    return ((Number) value).doubleValue() != 0.0;
                }
            }
        }
        return defaultValue;
    }

    /**
     * Extract string value from data map using multiple possible keys.
     */
    private String extractString(Map<String, Object> data, String... keys) {
        for (String key : keys) {
            Object value = data.get(key);
            if (value != null) {
                return value.toString();
            }
        }
        return null;
    }
}
