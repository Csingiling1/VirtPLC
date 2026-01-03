package com.virtplc.service;

import com.virtplc.model.Company;
import com.virtplc.model.Manufacturer;
import com.virtplc.model.SensorData;
import com.virtplc.model.PlcData;
import com.virtplc.repository.PlcDataRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Service for retrieving and managing sensor data.
 * Persists data to TimescaleDB and provides real-time and historical data
 * access.
 * Now uses flexible data collection from simulator API as primary source.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DataService {

    private final PlcDataRepository plcDataRepository;
    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Get the latest sensor data from plc_data table.
     */
    @Transactional
    public SensorData getLatestData(List<Manufacturer> manufacturers) {
        log.debug("Querying latest sensor data from plc_data table");

        SensorData.SensorDataBuilder builder = SensorData.builder()
                .timestamp(System.currentTimeMillis())
                .systemStatus("Running - MQTT Data Collection")
                .quality(95);

        // List of device_ids to query
        List<String> deviceIds = List.of(
                "motor_speed_PLC-NY-001", "motor_temp_PLC-NY-001",
                "motor_speed_PLC-NY-002", "motor_temp_PLC-NY-002",
                "Conveyor1_rpm", "Conveyor1_status",
                "Placer1_position", "Placer1_status");

        for (String deviceId : deviceIds) {
            PlcData latest = plcDataRepository.findLatestByDeviceId(deviceId);
            if (latest != null && latest.getData() != null) {
                try {
                    // The data field is already a JsonNode, so we can work with it directly
                    JsonNode dataNode = latest.getData();

                    // Check if it has signal_config (for MQTT data)
                    if (dataNode.has("signal_config")) {
                        JsonNode signalConfig = dataNode.get("signal_config");

                        // Map based on device_id
                        switch (deviceId) {
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
                    log.warn("Failed to parse data for device {}: {}", deviceId, e.getMessage());
                }
            }
        }

        return builder.build();
    }

    /**
     * Get historical data for a time range from TimescaleDB.
     */
    public List<SensorData> getDataRange(List<Manufacturer> manufacturers, Long startTime, Long endTime, int page,
            int size) {
        log.debug("Querying historical sensor data from plc_data table for range {} to {}", startTime, endTime);

        LocalDateTime start = LocalDateTime.ofEpochSecond(startTime / 1000, 0, ZoneOffset.UTC);
        LocalDateTime end = LocalDateTime.ofEpochSecond(endTime / 1000, 0, ZoneOffset.UTC);

        List<PlcData> plcDataList = plcDataRepository.findByTimestampBetween(start, end);

        // Group by timestamp and convert to SensorData
        Map<LocalDateTime, List<PlcData>> groupedByTime = plcDataList.stream()
                .collect(Collectors.groupingBy(PlcData::getTimestamp));

        return groupedByTime.entrySet().stream()
                .sorted(Map.Entry.<LocalDateTime, List<PlcData>>comparingByKey().reversed())
                .skip((long) page * size)
                .limit(size)
                .map(entry -> convertPlcDataListToSensorData(entry.getValue(), entry.getKey()))
                .collect(Collectors.toList());
    }

    /**
     * Get data for a specific device within a time range.
     */
    public List<SensorData> getDeviceData(Company company, String deviceId, Long startTime, Long endTime) {
        log.debug("Querying device data from plc_data table for device {} in range {} to {}", deviceId, startTime,
                endTime);

        LocalDateTime start = LocalDateTime.ofEpochSecond(startTime / 1000, 0, ZoneOffset.UTC);
        LocalDateTime end = LocalDateTime.ofEpochSecond(endTime / 1000, 0, ZoneOffset.UTC);

        List<PlcData> plcDataList = plcDataRepository.findByTimestampBetween(start, end).stream()
                .filter(data -> deviceId.equals(data.getDeviceId()))
                .collect(Collectors.toList());

        return plcDataList.stream()
                .map(plcData -> convertPlcDataListToSensorData(List.of(plcData), plcData.getTimestamp()))
                .collect(Collectors.toList());
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
}
