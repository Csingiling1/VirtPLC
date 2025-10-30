package com.virtplc.service;

import com.virtplc.model.Company;
import com.virtplc.model.SensorData;
import com.virtplc.model.SensorDataEntity;
import com.virtplc.opcua.NodeManager;
import com.virtplc.repository.CompanyRepository;
import com.virtplc.repository.SensorDataRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Map;
import java.util.Optional;
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
    private final CompanyRepository companyRepository;
    private final DataSourceService dataSourceService;
    private final FlexibleDataMapper dataMapper;
    private final Optional<NodeManager> nodeManager;

    /**
     * Get the latest sensor data from the configured data source and persist to
     * TimescaleDB.
     * Data source is determined by the 'data.source' property (simulator or plc).
     */
    @Transactional
    public SensorData getLatestData(Company company) {
        log.debug("Fetching latest sensor data from: {} for company: {}", dataSourceService.getDataSourceName(),
                company != null ? company.getName() : "all");

        SensorData sensorData;

        // Use the configured data source (simulator or PLC)
        if (dataSourceService.isAvailable()) {
            log.debug("Using {} as data source", dataSourceService.getDataSourceName());
            Map<String, Object> sourceData = dataSourceService.getLatestSensorData();
            sensorData = dataMapper.mapToSensorData(sourceData);
            log.debug("Successfully fetched data from {}", dataSourceService.getDataSourceName());
        } else {
            // Fallback to OPC-UA if available, otherwise hardcoded values
            if (nodeManager.isPresent()) {
                log.warn("Data source {} not available, falling back to OPC-UA", dataSourceService.getDataSourceName());
                NodeManager nm = nodeManager.get();
                sensorData = SensorData.builder()
                        .timestamp(System.currentTimeMillis())
                        .motor1Speed(nm.getMotor1Speed())
                        .motor1Temp(nm.getMotor1Temp())
                        .motor1Run(true)
                        .motor1Fault(false)
                        .motor2Speed(nm.getMotor2Speed())
                        .motor2Temp(nm.getMotor2Temp())
                        .motor2Run(true)
                        .motor2Fault(false)
                        .conveyor1Speed(nm.getConveyor1Speed())
                        .conveyor1Run(true)
                        .sensor1Value(nm.getSensor1Value())
                        .sensor2Value(nm.getSensor2Value())
                        .systemStatus("Running - OPC-UA Fallback")
                        .build();
            } else {
                log.warn("Data source {} not available and no OPC-UA fallback, using hardcoded values",
                        dataSourceService.getDataSourceName());
                sensorData = SensorData.builder()
                        .timestamp(System.currentTimeMillis())
                        .motor1Speed(0.0)
                        .motor1Temp(25.0)
                        .motor1Run(false)
                        .motor1Fault(true)
                        .motor2Speed(0.0)
                        .motor2Temp(25.0)
                        .motor2Run(false)
                        .motor2Fault(true)
                        .conveyor1Speed(0.0)
                        .conveyor1Run(false)
                        .sensor1Value(0.0)
                        .sensor2Value(false)
                        .systemStatus("Error - Data Source Unavailable")
                        .build();
            }
        }

        // Persist to TimescaleDB
        if (company != null) {
            try {
                SensorDataEntity entity = convertToEntity(sensorData, company);
                sensorDataRepository.save(entity);
                log.debug("Persisted sensor data to TimescaleDB: {} for company: {}", entity.getTimestamp(),
                        company.getName());
            } catch (Exception e) {
                log.error("Failed to persist sensor data to TimescaleDB", e);
            }
        }

        return sensorData;
    }

    /**
     * Get historical data for a time range from TimescaleDB.
     */
    public List<SensorData> getDataRange(Company company, Long startTime, Long endTime) {
        log.debug("Fetching data range from TimescaleDB: {} to {} for company: {}", startTime, endTime,
                company.getName());

        try {
            List<SensorDataEntity> entities = sensorDataRepository.findByCompanyAndTimestampBetween(
                    company,
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

    private SensorDataEntity convertToEntity(SensorData sensorData, Company company) {
        return SensorDataEntity.builder()
                .timestamp(LocalDateTime.ofInstant(java.time.Instant.ofEpochMilli(sensorData.getTimestamp()),
                        ZoneOffset.UTC))
                .deviceId("factory1") // Default device ID
                .company(company)
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
