package com.virtplc.pipeline;

import com.virtplc.grpc.GrpcDtos.SensorData;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

/**
 * Stream processor that integrates data pipeline with backpressure handling
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class StreamProcessor {

    private final DataPipelineService dataPipeline;
    private final BackpressureHandler backpressureHandler;

    /**
     * Process incoming sensor data stream with full pipeline
     */
    public Flux<SensorData> processSensorDataStream(Flux<SensorData> inputStream) {
        return backpressureHandler.withBackpressure(inputStream)
                .flatMap(data -> dataPipeline.ingestSensorData(data).thenReturn(data), 10) // Concurrent ingestion
                .doOnNext(data -> log.trace("Processed sensor data: {}", data.getSensorId()))
                .doOnError(error -> log.error("Error in stream processing", error));
    }

    /**
     * Get processed data stream for a specific sensor
     */
    public Flux<SensorData> getProcessedSensorData(String sensorId) {
        return backpressureHandler.withBackpressure(
                dataPipeline.getBufferedSensorData(sensorId));
    }

    /**
     * Get aggregated processed data stream
     */
    public Flux<SensorData> getAggregatedProcessedData() {
        return backpressureHandler.withBackpressure(
                dataPipeline.getAggregatedDataStream());
    }

    /**
     * Process batch data with pipeline
     */
    public Mono<Void> processSensorDataBatch(java.util.List<SensorData> batch) {
        return Flux.fromIterable(batch)
                .flatMap(data -> dataPipeline.ingestSensorData(data), 10) // Concurrent processing
                .then()
                .doOnSuccess(v -> log.debug("Processed batch of {} sensor data points", batch.size()))
                .doOnError(error -> log.error("Error processing sensor data batch", error));
    }

    /**
     * Get pipeline and backpressure statistics
     */
    public DataPipelineService.PipelineStats getPipelineStats() {
        return dataPipeline.getStats();
    }

    public BackpressureHandler.BackpressureStats getBackpressureStats() {
        return backpressureHandler.getStats();
    }

    /**
     * Combined statistics
     */
    public static class CombinedStats {
        public final DataPipelineService.PipelineStats pipelineStats;
        public final BackpressureHandler.BackpressureStats backpressureStats;

        public CombinedStats(DataPipelineService.PipelineStats pipelineStats,
                BackpressureHandler.BackpressureStats backpressureStats) {
            this.pipelineStats = pipelineStats;
            this.backpressureStats = backpressureStats;
        }
    }

    /**
     * Get combined statistics
     */
    public CombinedStats getCombinedStats() {
        return new CombinedStats(
                dataPipeline.getStats(),
                backpressureHandler.getStats());
    }

    /**
     * Reset all statistics
     */
    public void resetStats() {
        backpressureHandler.resetStats();
        log.info("Reset all stream processor statistics");
    }
}