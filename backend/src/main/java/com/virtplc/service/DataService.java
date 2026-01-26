package com.virtplc.service;

import com.virtplc.model.Company;
import com.virtplc.model.Device;
import com.virtplc.model.Manufacturer;
import com.virtplc.model.PlcData;
import com.virtplc.model.SensorData;
import com.virtplc.repository.DeviceRepository;
import com.virtplc.repository.PlcDataRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * Service for retrieving and managing sensor data.
 * Follows SOLID principles:
 * - Single Responsibility: Only orchestrates data retrieval operations
 * - Open/Closed: Extensible through strategy pattern for device mapping
 * - Liskov Substitution: Implements DataRetrievalService interface
 * - Interface Segregation: Separated concerns into focused interfaces
 * - Dependency Inversion: Depends on abstractions, not concretions
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DataService implements DataRetrievalService {

    private final PlcDataRepository plcDataRepository;
    private final DeviceRepository deviceRepository;
    private final DataMappingService dataMappingService;

    /**
     * Get the latest sensor data from plc_data table.
     * Only returns data if it's fresh (within device timeout period).
     * Delegates mapping logic to DataMappingService.
     */
    @Transactional(readOnly = true)
    @Override
    public SensorData getLatestData(List<Manufacturer> manufacturers) {
        log.debug("Querying latest sensor data from plc_data table");

        SensorData.SensorDataBuilder builder = SensorData.builder()
                .timestamp(System.currentTimeMillis())
                .systemStatus("Checking data freshness...")
                .quality(95);

        // Get active devices from database instead of hardcoded list
        List<Device> activeDevices = getActiveDevices();
        List<String> deviceIds = activeDevices.stream()
                .map(Device::getDeviceId)
                .collect(Collectors.toList());

        if (deviceIds.isEmpty()) {
            log.warn("No active devices configured in database");
            return builder.systemStatus("No devices configured").build();
        }

        boolean hasFreshData = false;
        int staleDataCount = 0;

        for (Device device : activeDevices) {
            try {
                var latestPlcData = plcDataRepository.findLatestByDeviceId(device.getDeviceId());
                if (latestPlcData != null) {
                    // Check if data is fresh based on device timeout
                    boolean isFresh = isDataFresh(latestPlcData, device.getDataTimeoutSeconds());
                    if (isFresh) {
                        // Delegate mapping to specialized service
                        var sensorData = dataMappingService.mapPlcDataToSensorData(latestPlcData);
                        // Merge the mapped data into our builder
                        mergeSensorData(builder, sensorData);
                        hasFreshData = true;
                    } else {
                        staleDataCount++;
                        log.debug("Stale data for device {}: age {} seconds (timeout: {}s)",
                                device.getDeviceId(),
                                java.time.Duration.between(latestPlcData.getTimestamp(),
                                        LocalDateTime.now()).getSeconds(),
                                device.getDataTimeoutSeconds());
                    }
                } else {
                    log.debug("No data found for device: {}", device.getDeviceId());
                }
            } catch (Exception e) {
                log.warn("Failed to process data for device {}: {}", device.getDeviceId(), e.getMessage());
            }
        }

        // Update system status based on data freshness
        if (hasFreshData) {
            builder.systemStatus("Running - Live Data Collection");
            builder.quality(Math.max(95 - (staleDataCount * 5), 50)); // Reduce quality for stale data
        } else if (staleDataCount > 0) {
            builder.systemStatus("Warning - Showing stale data (Unreal Engine may not be running)");
            builder.quality(30);
        } else {
            builder.systemStatus("No data available - Check Unreal Engine connection");
            builder.quality(0);
        }

        return builder.build();
    }

    /**
     * Get historical data for a time range from TimescaleDB.
     */
    @Transactional(readOnly = true)
    @Override
    public List<SensorData> getDataRange(List<Manufacturer> manufacturers, Long startTime, Long endTime, int page,
            int size) {
        log.debug("Querying historical sensor data from plc_data table for range {} to {}", startTime, endTime);

        LocalDateTime start = LocalDateTime.ofEpochSecond(startTime / 1000, 0, ZoneOffset.UTC);
        LocalDateTime end = LocalDateTime.ofEpochSecond(endTime / 1000, 0, ZoneOffset.UTC);

        var plcDataList = plcDataRepository.findByTimestampBetween(start, end);

        // Group by timestamp and convert to SensorData
        Map<LocalDateTime, List<com.virtplc.model.PlcData>> groupedByTime = plcDataList.stream()
                .collect(Collectors.groupingBy(com.virtplc.model.PlcData::getTimestamp));

        return groupedByTime.entrySet().stream()
                .sorted(Map.Entry.<LocalDateTime, List<com.virtplc.model.PlcData>>comparingByKey().reversed())
                .skip((long) page * size)
                .limit(size)
                .map(entry -> dataMappingService.mapPlcDataListToSensorData(entry.getValue(), entry.getKey()))
                .collect(Collectors.toList());
    }

    /**
     * Get data for a specific device within a time range.
     */
    @Transactional(readOnly = true)
    @Override
    public List<SensorData> getDeviceData(Company company, String deviceId, Long startTime, Long endTime) {
        log.debug("Querying device data from plc_data table for device {} in range {} to {}", deviceId, startTime,
                endTime);

        LocalDateTime start = LocalDateTime.ofEpochSecond(startTime / 1000, 0, ZoneOffset.UTC);
        LocalDateTime end = LocalDateTime.ofEpochSecond(endTime / 1000, 0, ZoneOffset.UTC);

        var plcDataList = plcDataRepository.findByTimestampBetween(start, end).stream()
                .filter(data -> deviceId.equals(data.getDeviceId()))
                .collect(Collectors.toList());

        return plcDataList.stream()
                .map(plcData -> dataMappingService.mapPlcDataToSensorData(plcData))
                .collect(Collectors.toList());
    }

    /**
     * Merges data from one SensorData into a builder.
     * Helper method to combine sensor data from multiple sources.
     */
    private void mergeSensorData(SensorData.SensorDataBuilder builder, SensorData source) {
        if (source.getMotor1Speed() != null) {
            builder.motor1Speed(source.getMotor1Speed());
        }
        if (source.getMotor1Temp() != null) {
            builder.motor1Temp(source.getMotor1Temp());
        }
        if (source.getMotor2Speed() != null) {
            builder.motor2Speed(source.getMotor2Speed());
        }
        if (source.getMotor2Temp() != null) {
            builder.motor2Temp(source.getMotor2Temp());
        }
        if (source.getConveyor1Speed() != null) {
            builder.conveyor1Speed(source.getConveyor1Speed());
        }
        if (source.getConveyor1Run() != null) {
            builder.conveyor1Run(source.getConveyor1Run());
        }
        if (source.getPlacer1Position() != null) {
            builder.placer1Position(source.getPlacer1Position());
        }
        if (source.getPlacer1Run() != null) {
            builder.placer1Run(source.getPlacer1Run());
        }
    }

    /**
     * Convert a list of PlcData entries at the same timestamp to a SensorData
     * object.
     */
    private SensorData convertPlcDataListToSensorData(List<PlcData> plcDataList, LocalDateTime timestamp) {
        SensorData.SensorDataBuilder builder = SensorData.builder()
                .timestamp(timestamp.toEpochSecond(ZoneOffset.UTC) * 1000)
                .systemStatus("Historical Data")
                .quality(95);

        for (PlcData plcData : plcDataList) {
            if (plcData.getData() != null) {
                try {
                    JsonNode dataNode = plcData.getData();

                    // Check if it has signal_config (for MQTT data)
                    if (dataNode.has("signal_config")) {
                        JsonNode signalConfig = dataNode.get("signal_config");

                        // Map based on device_id
                        switch (plcData.getDeviceId()) {
                            case "motor_speed_PLC-NY-001":
                                if (signalConfig.has("value") && !signalConfig.get("value").isNull()) {
                                    builder.motor1Speed(signalConfig.get("value").asDouble());
                                }
                                break;
                            case "motor_temp_PLC-NY-001":
                                if (signalConfig.has("value") && !signalConfig.get("value").isNull()) {
                                    builder.motor1Temp(signalConfig.get("value").asDouble());
                                }
                                break;
                            case "motor_speed_PLC-NY-002":
                                if (signalConfig.has("value") && !signalConfig.get("value").isNull()) {
                                    builder.motor2Speed(signalConfig.get("value").asDouble());
                                }
                                break;
                            case "motor_temp_PLC-NY-002":
                                if (signalConfig.has("value") && !signalConfig.get("value").isNull()) {
                                    builder.motor2Temp(signalConfig.get("value").asDouble());
                                }
                                break;
                            case "Conveyor1_rpm":
                                if (signalConfig.has("value") && !signalConfig.get("value").isNull()) {
                                    builder.conveyor1Speed(signalConfig.get("value").asDouble());
                                }
                                break;
                            case "Conveyor1_status":
                                if (signalConfig.has("isReady") && !signalConfig.get("isReady").isNull()) {
                                    builder.conveyor1Run(signalConfig.get("isReady").asBoolean());
                                }
                                break;
                        }
                    }
                } catch (Exception e) {
                    log.warn("Failed to parse data for device {}: {}", plcData.getDeviceId(), e.getMessage());
                }
            }
        }

        return builder.build();
    }

    /**
     * Get all active devices from database.
     */
    @Transactional(readOnly = true)
    private List<Device> getActiveDevices() {
        try {
            return deviceRepository.findByIsActiveTrue();
        } catch (Exception e) {
            log.warn("Failed to load active devices from database: {}", e.getMessage());
            return List.of(); // Return empty list as fallback
        }
    }

    /**
     * Check if PLC data is fresh based on device timeout configuration.
     */
    private boolean isDataFresh(com.virtplc.model.PlcData plcData, int timeoutSeconds) {
        if (plcData == null || plcData.getTimestamp() == null) {
            return false;
        }

        LocalDateTime dataTimestamp = plcData.getTimestamp();
        LocalDateTime now = LocalDateTime.now();
        long ageSeconds = java.time.Duration.between(dataTimestamp, now).getSeconds();

        return ageSeconds <= timeoutSeconds;
    }
}
