package com.virtplc.service;

import com.virtplc.model.Device;
import com.virtplc.model.DeviceMapping;
import com.virtplc.model.PlcData;
import com.virtplc.model.SensorData;
import com.virtplc.repository.DeviceMappingRepository;
import com.virtplc.repository.DeviceRepository;
import com.fasterxml.jackson.databind.JsonNode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Generic device mapping service using JPA configuration.
 * Supports any device type through database-driven configuration.
 */
@Slf4j
@Service
@Primary
@RequiredArgsConstructor
public class GenericDeviceMappingService implements DataMappingService {

    private final DeviceRepository deviceRepository;
    private final DeviceMappingRepository deviceMappingRepository;

    // Cache for device mappings to improve performance
    private final Map<String, List<DeviceMapping>> deviceMappingCache = new ConcurrentHashMap<>();

    @Override
    public SensorData mapPlcDataToSensorData(PlcData plcData) {
        SensorData.SensorDataBuilder builder = SensorData.builder()
                .timestamp(plcData.getTimestamp().toEpochSecond(java.time.ZoneOffset.UTC) * 1000)
                .systemStatus("Running - MQTT Data Collection")
                .quality(95);

        if (plcData.getData() != null) {
            mapDeviceData(builder, plcData.getDeviceId(), plcData.getData());
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
                mapDeviceData(builder, plcData.getDeviceId(), plcData.getData());
            }
        }

        return builder.build();
    }

    /**
     * Generic device data mapping using database configuration.
     */
    private void mapDeviceData(SensorData.SensorDataBuilder builder, String deviceId, JsonNode dataNode) {
        try {
            List<DeviceMapping> mappings = getDeviceMappings(deviceId);
            if (mappings.isEmpty()) {
                log.debug("No mappings found for device: {}", deviceId);
                return;
            }

            // Extract values from signal_config
            Double value = extractValueFromSignalConfig(dataNode);
            Boolean status = extractStatusFromSignalConfig(dataNode);

            // Apply each mapping configuration
            for (DeviceMapping mapping : mappings) {
                applyMapping(builder, mapping, value, status);
            }

        } catch (Exception e) {
            log.warn("Failed to map data for device {}: {}", deviceId, e.getMessage());
        }
    }

    /**
     * Get cached device mappings for a device ID.
     */
    private List<DeviceMapping> getDeviceMappings(String deviceId) {
        return deviceMappingCache.computeIfAbsent(deviceId, this::loadDeviceMappings);
    }

    /**
     * Load device mappings from database.
     */
    @Transactional(readOnly = true)
    private List<DeviceMapping> loadDeviceMappings(String deviceId) {
        return deviceMappingRepository.findByDevice_DeviceIdAndIsActiveTrue(deviceId);
    }

    /**
     * Apply a single mapping configuration to the sensor data builder.
     */
    private void applyMapping(SensorData.SensorDataBuilder builder, DeviceMapping mapping, Double value,
            Boolean status) {
        try {
            String fieldName = mapping.getFieldName();
            String fieldType = mapping.getFieldType();

            // Apply scaling and offset
            Double processedValue = value;
            if (processedValue != null) {
                processedValue = processedValue * mapping.getMultiplier() + mapping.getOffset();
            }

            // Map based on field type
            switch (fieldType.toLowerCase()) {
                case "numeric", "double", "float", "integer", "long" -> {
                    if (processedValue != null) {
                        setNumericField(builder, fieldName, processedValue);
                    }
                }
                case "boolean", "bool" -> {
                    if (status != null) {
                        setBooleanField(builder, fieldName, status);
                    }
                }
                case "string", "text" -> {
                    if (processedValue != null) {
                        setStringField(builder, fieldName, String.valueOf(processedValue));
                    }
                }
                default -> log.warn("Unknown field type: {} for field: {}", fieldType, fieldName);
            }

        } catch (Exception e) {
            log.warn("Failed to apply mapping for field {}: {}", mapping.getFieldName(), e.getMessage());
        }
    }

    /**
     * Set numeric field on SensorData builder using reflection.
     */
    private void setNumericField(SensorData.SensorDataBuilder builder, String fieldName, Double value) {
        try {
            // Use switch for known fields, fallback to dynamic mapping
            switch (fieldName) {
                case "motor1Speed" -> builder.motor1Speed(value);
                case "motor1Temp" -> builder.motor1Temp(value);
                case "motor2Speed" -> builder.motor2Speed(value);
                case "motor2Temp" -> builder.motor2Temp(value);
                case "conveyor1Rpm", "conveyor1Speed" -> builder.conveyor1Speed(value);
                case "conveyor1Status" -> builder.conveyor1Run(value != 0);
                case "placer1Position" -> builder.placer1Position(value);
                case "placer1Status" -> builder.placer1Run(value != 0);
                default -> {
                    // For unknown fields, we could extend SensorData or use a generic map
                    log.debug("Unknown numeric field: {}, value: {}", fieldName, value);
                }
            }
        } catch (Exception e) {
            log.warn("Failed to set numeric field {}: {}", fieldName, e.getMessage());
        }
    }

    /**
     * Set boolean field on SensorData builder.
     */
    private void setBooleanField(SensorData.SensorDataBuilder builder, String fieldName, Boolean value) {
        try {
            switch (fieldName) {
                case "motor1Status", "motor1Run" -> builder.motor1Run(value);
                case "motor2Status", "motor2Run" -> builder.motor2Run(value);
                case "conveyor1Status", "conveyor1Run" -> builder.conveyor1Run(value);
                case "placer1Status", "placer1Run" -> builder.placer1Run(value);
                default -> {
                    log.debug("Unknown boolean field: {}, value: {}", fieldName, value);
                }
            }
        } catch (Exception e) {
            log.warn("Failed to set boolean field {}: {}", fieldName, e.getMessage());
        }
    }

    /**
     * Set string field on SensorData builder.
     */
    private void setStringField(SensorData.SensorDataBuilder builder, String fieldName, String value) {
        try {
            // SensorData doesn't have many string fields, but we can add them as needed
            log.debug("String field mapping not implemented for: {}, value: {}", fieldName, value);
        } catch (Exception e) {
            log.warn("Failed to set string field {}: {}", fieldName, e.getMessage());
        }
    }

    /**
     * Maps device-specific data based on device ID.
     */
    @Override
    public void mapDeviceSpecificData(SensorData.SensorDataBuilder builder, String deviceId, JsonNode dataNode) {
        // For now, delegate to the existing mapping logic
        mapDeviceData(builder, deviceId, dataNode);
    }

    /**
     * Extract numeric value from signal_config JSON.
     */
    @Override
    public Double extractValueFromSignalConfig(JsonNode dataNode) {
        try {
            if (dataNode.has("signal_config") && dataNode.get("signal_config").has("value")) {
                JsonNode valueNode = dataNode.get("signal_config").get("value");
                if (valueNode.isNumber()) {
                    return valueNode.asDouble();
                } else if (valueNode.isTextual()) {
                    return Double.parseDouble(valueNode.asText());
                }
            }
        } catch (Exception e) {
            log.debug("Failed to extract value from signal_config: {}", e.getMessage());
        }
        return null;
    }

    /**
     * Extract boolean status from signal_config JSON.
     */
    @Override
    public Boolean extractStatusFromSignalConfig(JsonNode dataNode) {
        try {
            if (dataNode.has("signal_config") && dataNode.get("signal_config").has("status")) {
                JsonNode statusNode = dataNode.get("signal_config").get("status");
                if (statusNode.isBoolean()) {
                    return statusNode.asBoolean();
                } else if (statusNode.isNumber()) {
                    return statusNode.asInt() != 0;
                }
            }
        } catch (Exception e) {
            log.debug("Failed to extract status from signal_config: {}", e.getMessage());
        }
        return null;
    }

    /**
     * Clear mapping cache - call this when device mappings are updated.
     */
    public void clearMappingCache() {
        deviceMappingCache.clear();
        log.info("Device mapping cache cleared");
    }

    /**
     * Get all active devices for data collection.
     */
    @Transactional(readOnly = true)
    public List<Device> getActiveDevices() {
        return deviceRepository.findByIsActiveTrue();
    }
}