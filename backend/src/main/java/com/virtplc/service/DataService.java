package com.virtplc.service;

import com.virtplc.model.Company;
import com.virtplc.model.Manufacturer;
import com.virtplc.model.SensorData;
import com.virtplc.model.SensorDataEntity;
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
 * Now uses flexible data collection from simulator API as primary source.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DataService {

    private final SensorDataRepository sensorDataRepository;

    /**
     * Get the latest sensor data. Since data is now collected via MQTT and stored
     * by the collector service, this returns mock data for API compatibility.
     * TODO: Update API to query plc_data table directly.
     */
    @Transactional
    public SensorData getLatestData(List<Manufacturer> manufacturers) {
        log.debug("Returning mock sensor data (MQTT data stored by collector)");

        // Return mock data for API compatibility
        // In the future, this should query the plc_data table
        SensorData sensorData = SensorData.builder()
                .timestamp(System.currentTimeMillis())
                .motor1Speed(1500.0)
                .motor1Temp(45.0)
                .motor1Run(true)
                .motor1Fault(false)
                .motor2Speed(1200.0)
                .motor2Temp(42.0)
                .motor2Run(true)
                .motor2Fault(false)
                .conveyor1Speed(50.0)
                .conveyor1Run(true)
                .sensor1Value(25.5)
                .sensor2Value(true)
                .systemStatus("Running - MQTT Data Collection")
                .quality(95)
                .build();

        return sensorData;
    }

    /**
     * Get historical data for a time range from TimescaleDB.
     */
    public List<SensorData> getDataRange(List<Manufacturer> manufacturers, Long startTime, Long endTime, int page,
            int size) {
        if (manufacturers == null) {
            // Admin user - get all data
            return getAllDataRange(startTime, endTime, page, size);
        } else {
            // Non-admin user - get data for their manufacturers
            return getDataRangeForManufacturers(manufacturers, startTime, endTime, page, size);
        }
    }

    private List<SensorData> getAllDataRange(Long startTime, Long endTime, int page, int size) {
        log.debug("Fetching all data range from TimescaleDB: {} to {} (page: {}, size: {})", startTime, endTime, page,
                size);

        try {
            List<SensorDataEntity> entities = sensorDataRepository.findByTimestampBetween(
                    LocalDateTime.ofInstant(java.time.Instant.ofEpochMilli(startTime), ZoneOffset.UTC),
                    LocalDateTime.ofInstant(java.time.Instant.ofEpochMilli(endTime), ZoneOffset.UTC));

            return entities.stream()
                    .skip((long) page * size)
                    .limit(size)
                    .map(this::convertToSensorData)
                    .collect(Collectors.toList());

        } catch (Exception e) {
            log.error("Failed to query TimescaleDB for all historical data", e);
            return List.of();
        }
    }

    private List<SensorData> getDataRangeForManufacturers(List<Manufacturer> manufacturers, Long startTime,
            Long endTime, int page, int size) {
        log.debug("Fetching data range from TimescaleDB: {} to {} for {} manufacturers (page: {}, size: {})", startTime,
                endTime,
                manufacturers.size(), page, size);

        try {
            // Get companies from manufacturers
            List<Company> companies = manufacturers.stream()
                    .map(Manufacturer::getCompany)
                    .distinct()
                    .collect(Collectors.toList());

            // For now, assume all manufacturers belong to the same company
            Company company = companies.get(0);

            List<SensorDataEntity> entities = sensorDataRepository.findByCompanyAndTimestampBetween(
                    company,
                    LocalDateTime.ofInstant(java.time.Instant.ofEpochMilli(startTime), ZoneOffset.UTC),
                    LocalDateTime.ofInstant(java.time.Instant.ofEpochMilli(endTime), ZoneOffset.UTC));

            return entities.stream()
                    .skip((long) page * size)
                    .limit(size)
                    .map(this::convertToSensorData)
                    .collect(Collectors.toList());

        } catch (Exception e) {
            log.error("Failed to query TimescaleDB for historical data", e);
            return List.of();
        }
    }

    /**
     * Get data for a specific device within a time range.
     */
    public List<SensorData> getDeviceData(Company company, String deviceId, Long startTime, Long endTime) {
        log.debug("Fetching device data from TimescaleDB: {} from {} to {} for company: {}", deviceId, startTime,
                endTime, company.getName());

        try {
            List<SensorDataEntity> entities = sensorDataRepository.findByCompanyAndDeviceIdAndTimestampBetween(
                    company,
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
