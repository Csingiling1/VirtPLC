package com.virtplc.grpc;

import com.virtplc.grpc.GrpcDtos.*;
import com.virtplc.grpc.GrpcServices.SensorDataService;
import com.virtplc.model.SensorDataEntity;
import com.virtplc.repository.SensorDataRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.stream.Stream;

/**
 * Service implementation for sensor data operations
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class SensorDataServiceGrpcImpl implements SensorDataService {

    private final SensorDataProcessor sensorDataProcessor;
    private final SensorDataRepository sensorDataRepository;

    @Override
    public Flux<SensorData> streamSensorData() {
        log.info("Starting sensor data stream");
        return sensorDataProcessor.getSensorDataStream();
    }

    @Override
    public Mono<Void> uploadSensorDataBatch(SensorDataBatch batch) {
        log.info("Processing sensor data batch with {} records", batch.getData().size());

        return sensorDataProcessor.processSensorDataBatch(batch.getData(), batch.getBatchId());
    }

    @Override
    public Flux<SensorData> getSensorDataHistory(SensorDataQuery query) {
        log.info("Fetching historical data for sensor {} from {} to {}",
                query.getSensorId(), query.getStartTime(), query.getEndTime());

        LocalDateTime startTime = LocalDateTime.ofInstant(Instant.ofEpochMilli(query.getStartTime()), ZoneOffset.UTC);
        LocalDateTime endTime = LocalDateTime.ofInstant(Instant.ofEpochMilli(query.getEndTime()), ZoneOffset.UTC);

        List<SensorDataEntity> entities;
        if (query.getSensorId() != null && !query.getSensorId().isEmpty()) {
            entities = sensorDataRepository.findByDeviceIdAndTimestampBetween(
                    query.getSensorId(), startTime, endTime);
        } else {
            entities = sensorDataRepository.findByTimestampBetween(startTime, endTime);
        }

        // Convert entities to DTOs - create multiple sensor readings per entity
        List<SensorData> sensorDataList = entities.stream()
                .flatMap(this::convertEntityToSensorData)
                .toList();

        return Flux.fromIterable(sensorDataList);
    }

    /**
     * Convert a SensorDataEntity to multiple SensorData DTOs (one for each motor/sensor reading)
     */
    private Stream<SensorData> convertEntityToSensorData(SensorDataEntity entity) {
        return Stream.of(
                createSensorData(entity, "motor1_speed", entity.getMotor1Speed()),
                createSensorData(entity, "motor1_temp", entity.getMotor1Temp()),
                createSensorData(entity, "motor1_run", entity.getMotor1Run() != null ? (entity.getMotor1Run() ? 1.0 : 0.0) : null),
                createSensorData(entity, "motor1_fault", entity.getMotor1Fault() != null ? (entity.getMotor1Fault() ? 1.0 : 0.0) : null),
                createSensorData(entity, "motor2_speed", entity.getMotor2Speed()),
                createSensorData(entity, "motor2_temp", entity.getMotor2Temp()),
                createSensorData(entity, "motor2_run", entity.getMotor2Run() != null ? (entity.getMotor2Run() ? 1.0 : 0.0) : null),
                createSensorData(entity, "motor2_fault", entity.getMotor2Fault() != null ? (entity.getMotor2Fault() ? 1.0 : 0.0) : null)
        ).filter(sensorData -> sensorData != null);
    }

    /**
     * Create a SensorData DTO for a specific sensor reading
     */
    private SensorData createSensorData(SensorDataEntity entity, String sensorId, Double value) {
        if (value == null) return null;

        return SensorData.builder()
                .sensorId(sensorId)
                .deviceId(entity.getDeviceId())
                .value(value)
                .timestamp(entity.getTimestamp().toInstant(ZoneOffset.UTC).toEpochMilli())
                .build();
    }
}