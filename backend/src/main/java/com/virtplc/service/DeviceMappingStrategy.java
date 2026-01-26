package com.virtplc.service;

import com.virtplc.model.PlcData;
import com.virtplc.model.SensorData;
import com.fasterxml.jackson.databind.JsonNode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Legacy implementation - kept for reference.
 * Use GenericDeviceMappingService for new implementations.
 */
@Service("legacyDataMappingService")
@Slf4j
public class DeviceMappingStrategy implements DataMappingService {

    @Override
    public SensorData mapPlcDataToSensorData(PlcData plcData) {
        SensorData.SensorDataBuilder builder = SensorData.builder()
                .timestamp(plcData.getTimestamp().toEpochSecond(java.time.ZoneOffset.UTC) * 1000)
                .systemStatus("Running - MQTT Data Collection")
                .quality(95);

        if (plcData.getData() != null) {
            mapDeviceSpecificData(builder, plcData.getDeviceId(), plcData.getData());
        }

        return builder.build();
    }

    @Override
    public SensorData mapPlcDataListToSensorData(List<PlcData> plcDataList, LocalDateTime timestamp) {
        SensorData.SensorDataBuilder builder = SensorData.builder()
                .timestamp(timestamp.toEpochSecond(java.time.ZoneOffset.UTC) * 1000)
                .systemStatus("Running - MQTT Data Collection")
                .quality(95);

        for (PlcData plcData : plcDataList) {
            if (plcData.getData() != null) {
                mapDeviceSpecificData(builder, plcData.getDeviceId(), plcData.getData());
            }
        }

        return builder.build();
    }

    @Override
    public Double extractValueFromSignalConfig(JsonNode signalConfig) {
        if (signalConfig != null && signalConfig.has("value") && !signalConfig.get("value").isNull()) {
            return signalConfig.get("value").asDouble();
        }
        return null;
    }

    @Override
    public Boolean extractStatusFromSignalConfig(JsonNode signalConfig) {
        if (signalConfig != null && signalConfig.has("isReady") && !signalConfig.get("isReady").isNull()) {
            return signalConfig.get("isReady").asBoolean();
        }
        return null;
    }

    @Override
    public void mapDeviceSpecificData(SensorData.SensorDataBuilder builder, String deviceId, JsonNode dataNode) {
        try {
            if (!dataNode.has("signal_config")) {
                return;
            }

            JsonNode signalConfig = dataNode.get("signal_config");
            Double value = extractValueFromSignalConfig(signalConfig);
            Boolean status = extractStatusFromSignalConfig(signalConfig);

            // Use strategy pattern for device mapping
            MappingStrategy strategy = getDeviceMappingStrategy(deviceId);
            strategy.map(builder, value, status);

        } catch (Exception e) {
            log.warn("Failed to map data for device {}: {}", deviceId, e.getMessage());
        }
    }

    /**
     * Factory method for device mapping strategies.
     * Follows Open/Closed Principle - new devices can be added without modifying
     * existing code.
     */
    private MappingStrategy getDeviceMappingStrategy(String deviceId) {
        return switch (deviceId) {
            case "motor_speed_PLC-NY-001" -> new Motor1SpeedMapping();
            case "motor_temp_PLC-NY-001" -> new Motor1TempMapping();
            case "motor_speed_PLC-NY-002" -> new Motor2SpeedMapping();
            case "motor_temp_PLC-NY-002" -> new Motor2TempMapping();
            case "Conveyor1_rpm" -> new Conveyor1SpeedMapping();
            case "Conveyor1_status" -> new Conveyor1StatusMapping();
            case "Placer1_position" -> new Placer1PositionMapping();
            case "Placer1_status" -> new Placer1StatusMapping();
            default -> new DefaultMapping(deviceId);
        };
    }

    /**
     * Strategy interface for device-specific mapping.
     */
    private interface MappingStrategy {
        void map(SensorData.SensorDataBuilder builder, Double value, Boolean status);
    }

    /**
     * Motor 1 speed mapping strategy.
     */
    private static class Motor1SpeedMapping implements MappingStrategy {
        @Override
        public void map(SensorData.SensorDataBuilder builder, Double value, Boolean status) {
            if (value != null) {
                builder.motor1Speed(value);
            }
        }
    }

    /**
     * Motor 1 temperature mapping strategy.
     */
    private static class Motor1TempMapping implements MappingStrategy {
        @Override
        public void map(SensorData.SensorDataBuilder builder, Double value, Boolean status) {
            if (value != null) {
                builder.motor1Temp(value);
            }
        }
    }

    /**
     * Motor 2 speed mapping strategy.
     */
    private static class Motor2SpeedMapping implements MappingStrategy {
        @Override
        public void map(SensorData.SensorDataBuilder builder, Double value, Boolean status) {
            if (value != null) {
                builder.motor2Speed(value);
            }
        }
    }

    /**
     * Motor 2 temperature mapping strategy.
     */
    private static class Motor2TempMapping implements MappingStrategy {
        @Override
        public void map(SensorData.SensorDataBuilder builder, Double value, Boolean status) {
            if (value != null) {
                builder.motor2Temp(value);
            }
        }
    }

    /**
     * Conveyor 1 speed mapping strategy.
     */
    private static class Conveyor1SpeedMapping implements MappingStrategy {
        @Override
        public void map(SensorData.SensorDataBuilder builder, Double value, Boolean status) {
            if (value != null) {
                builder.conveyor1Speed(value);
            }
        }
    }

    /**
     * Conveyor 1 status mapping strategy.
     */
    private static class Conveyor1StatusMapping implements MappingStrategy {
        @Override
        public void map(SensorData.SensorDataBuilder builder, Double value, Boolean status) {
            if (status != null) {
                builder.conveyor1Run(status);
            }
        }
    }

    /**
     * Placer 1 position mapping strategy.
     */
    private static class Placer1PositionMapping implements MappingStrategy {
        @Override
        public void map(SensorData.SensorDataBuilder builder, Double value, Boolean status) {
            if (value != null) {
                builder.placer1Position(value);
            }
        }
    }

    /**
     * Placer 1 status mapping strategy.
     */
    private static class Placer1StatusMapping implements MappingStrategy {
        @Override
        public void map(SensorData.SensorDataBuilder builder, Double value, Boolean status) {
            if (status != null) {
                builder.placer1Run(status);
            }
        }
    }

    /**
     * Default mapping strategy for unknown devices.
     */
    private static class DefaultMapping implements MappingStrategy {
        private final String deviceId;

        public DefaultMapping(String deviceId) {
            this.deviceId = deviceId;
        }

        @Override
        public void map(SensorData.SensorDataBuilder builder, Double value, Boolean status) {
            log.debug("No specific mapping found for device: {}", deviceId);
        }
    }
}