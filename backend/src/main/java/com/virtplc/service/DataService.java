package com.virtplc.service;

import com.virtplc.model.SensorData;
import com.virtplc.model.SensorDataEntity;
import com.virtplc.opcua.NodeManager;
import com.virtplc.repository.SensorDataRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Service for retrieving and managing sensor data.
 * Persists data to TimescaleDB and provides real-time and historical data
 * access.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DataService {

    private final NodeManager nodeManager;
    private final SensorDataRepository sensorDataRepository;

    /**
     * Get the latest sensor data from OPC-UA nodes and persist to TimescaleDB.
     */
    @Transactional
    public SensorData getLatestData() {
        log.debug("Fetching latest sensor data");

        SensorData sensorData = SensorData.builder()
                .timestamp(System.currentTimeMillis())
                .motor1Speed(nodeManager.getMotor1Speed())
                .motor1Temp(nodeManager.getMotor1Temp())
                .motor1Run(true)
                .motor1Fault(false)
                .motor2Speed(nodeManager.getMotor2Speed())
                .motor2Temp(nodeManager.getMotor2Temp())
                .motor2Run(true)
                .motor2Fault(false)
                .conveyor1Speed(nodeManager.getConveyor1Speed())
                .conveyor1Run(true)
                .sensor1Value(nodeManager.getSensor1Value())
                .sensor2Value(nodeManager.getSensor2Value())
                .systemStatus("Running")
                .build();

        // Persist to TimescaleDB
        try {
            SensorDataEntity entity = convertToEntity(sensorData);
            sensorDataRepository.save(entity);
            log.debug("Persisted sensor data to TimescaleDB: {}", entity.getTimestamp());
        } catch (Exception e) {
            log.error("Failed to persist sensor data to TimescaleDB", e);
        }

        return sensorData;
    }

    /**
     * Get historical data for a time range from TimescaleDB.
     */
    public List<SensorData> getDataRange(Long startTime, Long endTime) {
        log.debug("Fetching data range from TimescaleDB: {} to {}", startTime, endTime);

        try {
            List<SensorDataEntity> entities = sensorDataRepository.findByTimestampBetween(
                    LocalDateTime.ofInstant(java.time.Instant.ofEpochMilli(startTime), ZoneOffset.UTC),
                    LocalDateTime.ofInstant(java.time.Instant.ofEpochMilli(endTime), ZoneOffset.UTC));

            return entities.stream()
                    .map(this::convertToSensorData)
                    .collect(Collectors.toList());

        } catch (Exception e) {
            log.error("Failed to query TimescaleDB for historical data", e);
            // Return empty list on error
            return List.of();
        }
    }

    /**
     * Get data for a specific device within a time range.
     */
    public List<SensorData> getDeviceData(String deviceId, Long startTime, Long endTime) {
        log.debug("Fetching device data from TimescaleDB: {} from {} to {}", deviceId, startTime, endTime);

        try {
            List<SensorDataEntity> entities = sensorDataRepository.findByDeviceIdAndTimestampBetween(
                    deviceId,
                    LocalDateTime.ofInstant(java.time.Instant.ofEpochMilli(startTime), ZoneOffset.UTC),
                    LocalDateTime.ofInstant(java.time.Instant.ofEpochMilli(endTime), ZoneOffset.UTC));

            return entities.stream()
                    .map(this::convertToSensorData)
                    .collect(Collectors.toList());

        } catch (Exception e) {
            log.error("Failed to query TimescaleDB for device data", e);
            return List.of();
        }
    }

    private SensorDataEntity convertToEntity(SensorData sensorData) {
        return SensorDataEntity.builder()
                .timestamp(LocalDateTime.ofInstant(java.time.Instant.ofEpochMilli(sensorData.getTimestamp()),
                        ZoneOffset.UTC))
                .deviceId("factory1") // Default device ID
                .motor1Speed(sensorData.getMotor1Speed())
                .motor1Temp(sensorData.getMotor1Temp())
                .motor1Run(sensorData.getMotor1Run())
                .motor1Fault(sensorData.getMotor1Fault())
                .motor2Speed(sensorData.getMotor2Speed())
                .motor2Temp(sensorData.getMotor2Temp())
                .motor2Run(sensorData.getMotor2Run())
                .motor2Fault(sensorData.getMotor2Fault())
                .conveyor1Speed(sensorData.getConveyor1Speed())
                .conveyor1Run(sensorData.getConveyor1Run())
                .sensor1Value(sensorData.getSensor1Value())
                .sensor2Value(sensorData.getSensor2Value())
                .systemStatus(sensorData.getSystemStatus())
                .build();
    }

    private SensorData convertToSensorData(SensorDataEntity entity) {
        return SensorData.builder()
                .timestamp(entity.getTimestamp().toInstant(ZoneOffset.UTC).toEpochMilli())
                .motor1Speed(entity.getMotor1Speed())
                .motor1Temp(entity.getMotor1Temp())
                .motor1Run(entity.getMotor1Run())
                .motor1Fault(entity.getMotor1Fault())
                .motor2Speed(entity.getMotor2Speed())
                .motor2Temp(entity.getMotor2Temp())
                .motor2Run(entity.getMotor2Run())
                .motor2Fault(entity.getMotor2Fault())
                .conveyor1Speed(entity.getConveyor1Speed())
                .conveyor1Run(entity.getConveyor1Run())
                .sensor1Value(entity.getSensor1Value())
                .sensor2Value(entity.getSensor2Value())
                .systemStatus(entity.getSystemStatus())
                .build();
    }
}
