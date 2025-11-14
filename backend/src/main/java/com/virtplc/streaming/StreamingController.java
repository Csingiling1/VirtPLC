package com.virtplc.streaming;

import com.virtplc.grpc.GrpcDtos.SensorData;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

/**
 * REST controller for real-time data streaming
 */
@Slf4j
@RestController
@RequestMapping("/api/streaming")
@RequiredArgsConstructor
@ConditionalOnProperty(name = "opcua.client.enabled", havingValue = "true")
public class StreamingController {

    private final BackpressureAwareDataSource dataSource;
    private final DataPipelineProcessor dataPipeline;

    /**
     * Start simulated data stream
     */
    @GetMapping(value = "/data/simulated", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<SensorData> streamSimulatedData(
            @RequestParam(defaultValue = "10") int ratePerSecond,
            @RequestParam(defaultValue = "60") int durationSeconds) {

        log.info("Starting simulated data stream: {} data points/second for {} seconds", ratePerSecond,
                durationSeconds);

        return dataSource.generateSensorDataStream(ratePerSecond)
                .take(java.time.Duration.ofSeconds(durationSeconds))
                .doOnComplete(() -> log.info("Simulated data stream completed"))
                .doOnCancel(() -> log.info("Simulated data stream cancelled"));
    }

    /**
     * Get buffered data for a specific sensor
     */
    @GetMapping(value = "/data/buffered/{sensorId}", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<SensorData> streamBufferedData(@PathVariable String sensorId) {
        log.info("Streaming buffered data for sensor: {}", sensorId);

        return dataPipeline.getBufferedDataStream(sensorId)
                .doOnComplete(() -> log.info("Buffered data stream completed for sensor: {}", sensorId))
                .doOnCancel(() -> log.info("Buffered data stream cancelled for sensor: {}", sensorId));
    }

    /**
     * Get batched data with windowing
     */
    @GetMapping(value = "/data/batched/{sensorId}", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<java.util.List<SensorData>> streamBatchedData(
            @PathVariable String sensorId,
            @RequestParam(defaultValue = "5000") long windowMs) {

        log.info("Streaming batched data for sensor: {} with {}ms windows", sensorId, windowMs);

        return dataPipeline.getBatchedDataStream(sensorId, java.time.Duration.ofMillis(windowMs))
                .doOnNext(batch -> log.debug("Sent batch of {} items for sensor {}", batch.size(), sensorId))
                .doOnComplete(() -> log.info("Batched data stream completed for sensor: {}", sensorId))
                .doOnCancel(() -> log.info("Batched data stream cancelled for sensor: {}", sensorId));
    }

    /**
     * Connect to external data source
     */
    @PostMapping("/connect")
    public Flux<SensorData> connectToExternalSource(
            @RequestParam String sourceUrl,
            @RequestBody java.util.List<String> sensorIds) {

        log.info("Connecting to external data source: {} for sensors: {}", sourceUrl, sensorIds);

        return dataSource.connectToExternalSource(sourceUrl, sensorIds)
                .doOnComplete(() -> log.info("External data source connection completed"))
                .doOnCancel(() -> log.info("External data source connection cancelled"));
    }

    /**
     * Get streaming statistics
     */
    @GetMapping("/stats")
    public StreamingStats getStreamingStats() {
        var dataSourceStats = dataSource.getStats();
        var pipelineStats = dataPipeline.getStats();

        return new StreamingStats(dataSourceStats, pipelineStats);
    }

    /**
     * Clear all buffers (admin operation)
     */
    @PostMapping("/clear")
    public void clearBuffers() {
        log.info("Clearing all streaming buffers");
        dataPipeline.clearBuffers();
    }

    /**
     * Streaming statistics response
     */
    public static class StreamingStats {
        public final BackpressureAwareDataSource.DataSourceStats dataSource;
        public final DataPipelineProcessor.PipelineStats pipeline;

        public StreamingStats(BackpressureAwareDataSource.DataSourceStats dataSource,
                DataPipelineProcessor.PipelineStats pipeline) {
            this.dataSource = dataSource;
            this.pipeline = pipeline;
        }
    }
}