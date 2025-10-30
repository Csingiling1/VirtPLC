package com.virtplc.grpc;

import com.virtplc.grpc.GrpcDtos.SensorData;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import org.springframework.stereotype.Repository;
import reactor.core.publisher.Flux;

import java.time.Instant;

/**
 * Reactive repository for sensor data
 */
@Repository
public interface SensorDataRepository extends ReactiveCrudRepository<SensorData, String> {

    /**
     * Find sensor data by sensor ID
     */
    Flux<SensorData> findBySensorId(String sensorId);

    /**
     * Find sensor data within time range
     */
    Flux<SensorData> findByTimestampBetween(Instant startTime, Instant endTime);

    /**
     * Find sensor data by sensor ID and time range
     */
    Flux<SensorData> findBySensorIdAndTimestampBetween(String sensorId, Instant startTime, Instant endTime);
}