package com.virtplc.grpc;

import com.virtplc.grpc.GrpcDtos.*;
import com.virtplc.grpc.GrpcServices.SensorDataService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.Instant;

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

        Instant startTime = Instant.ofEpochMilli(query.getStartTime());
        Instant endTime = Instant.ofEpochMilli(query.getEndTime());

        if (query.getSensorId() != null && !query.getSensorId().isEmpty()) {
            return sensorDataRepository.findBySensorIdAndTimestampBetween(
                    query.getSensorId(), startTime, endTime);
        } else {
            return sensorDataRepository.findByTimestampBetween(startTime, endTime);
        }
    }
}