package com.virtplc.grpc;

import com.virtplc.grpc.GrpcDtos.*;
import com.virtplc.pipeline.StreamProcessor;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.List;

/**
 * Real-time sensor data processor with pipeline integration
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class SensorDataProcessor {

    private final StreamProcessor streamProcessor;

    /**
     * Get real-time sensor data stream through pipeline
     */
    public Flux<SensorData> getSensorDataStream() {
        // This would connect to OPC-UA server or message queue
        // For now, return aggregated processed data from pipeline
        return streamProcessor.getAggregatedProcessedData();
    }

    /**
     * Process batch of sensor data through pipeline
     */
    public Mono<Void> processSensorDataBatch(List<SensorData> data, long batchId) {
        log.info("Processing batch {} with {} records through pipeline", batchId, data.size());

        return streamProcessor.processSensorDataBatch(data)
                .doOnSuccess(v -> log.debug("Successfully processed batch {} through pipeline", batchId))
                .doOnError(error -> log.error("Error processing batch {} through pipeline", batchId, error));
    }
}