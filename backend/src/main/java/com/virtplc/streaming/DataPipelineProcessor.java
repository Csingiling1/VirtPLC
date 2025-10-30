package com.virtplc.streaming;

import com.virtplc.grpc.GrpcDtos.SensorData;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Scheduler;

import java.time.Duration;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Real-time data pipeline with buffering and backpressure handling
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class DataPipelineProcessor {

    private final Scheduler dataProcessingScheduler;
    private final ConcurrentHashMap<String, ConcurrentLinkedQueue<SensorData>> sensorBuffers = new ConcurrentHashMap<>();
    private final AtomicLong processedCount = new AtomicLong(0);
    private final AtomicLong droppedCount = new AtomicLong(0);

    private static final int MAX_BUFFER_SIZE = 10000; // Max buffer size per sensor
    private static final int BATCH_SIZE = 100; // Process in batches

    /**
     * Process incoming sensor data stream with backpressure
     */
    public Flux<SensorData> processDataStream(Flux<SensorData> inputStream) {
        return inputStream
                .doOnNext(this::bufferData)
                .onBackpressureBuffer(MAX_BUFFER_SIZE, data -> {
                    droppedCount.incrementAndGet();
                    log.warn("Backpressure: Dropped sensor data for {}", data.getSensorId());
                })
                .publishOn(dataProcessingScheduler)
                .doOnNext(data -> processedCount.incrementAndGet())
                .doOnError(error -> log.error("Error in data pipeline", error));
    }

    /**
     * Get buffered data stream for a specific sensor
     */
    public Flux<SensorData> getBufferedDataStream(String sensorId) {
        return Flux.interval(Duration.ofMillis(50)) // Poll every 50ms
                .flatMap(tick -> drainBuffer(sensorId))
                .filter(data -> !data.isEmpty())
                .flatMapIterable(list -> list) // Flatten the list
                .onBackpressureLatest() // Drop older data if consumer is slow
                .publishOn(dataProcessingScheduler);
    }

    /**
     * Get batched data stream with windowing
     */
    public Flux<java.util.List<SensorData>> getBatchedDataStream(String sensorId, Duration windowDuration) {
        return getBufferedDataStream(sensorId)
                .window(windowDuration)
                .flatMap(window -> window.collectList())
                .filter(list -> !list.isEmpty())
                .onBackpressureBuffer(10, list -> {
                    log.warn("Batch backpressure: Dropping batch of {} items for sensor {}", list.size(), sensorId);
                });
    }

    /**
     * Buffer incoming sensor data
     */
    private void bufferData(SensorData data) {
        String sensorId = data.getSensorId();
        ConcurrentLinkedQueue<SensorData> buffer = sensorBuffers.computeIfAbsent(sensorId,
                k -> new ConcurrentLinkedQueue<>());

        // Check buffer size and drop oldest if full
        if (buffer.size() >= MAX_BUFFER_SIZE) {
            SensorData dropped = buffer.poll();
            if (dropped != null) {
                droppedCount.incrementAndGet();
                log.warn("Buffer full for sensor {}, dropped oldest data", sensorId);
            }
        }

        buffer.offer(data);
    }

    /**
     * Drain buffer for a sensor (thread-safe)
     */
    private Mono<java.util.List<SensorData>> drainBuffer(String sensorId) {
        return Mono.fromCallable(() -> {
            ConcurrentLinkedQueue<SensorData> buffer = sensorBuffers.get(sensorId);
            if (buffer == null || buffer.isEmpty()) {
                return java.util.Collections.emptyList();
            }

            java.util.List<SensorData> batch = new java.util.ArrayList<>();
            SensorData data;
            while ((data = buffer.poll()) != null && batch.size() < BATCH_SIZE) {
                batch.add(data);
            }

            return batch;
        });
    }

    /**
     * Get pipeline statistics
     */
    public PipelineStats getStats() {
        long totalBuffered = sensorBuffers.values().stream()
                .mapToLong(ConcurrentLinkedQueue::size)
                .sum();

        return new PipelineStats(
                processedCount.get(),
                droppedCount.get(),
                totalBuffered,
                sensorBuffers.size());
    }

    /**
     * Clear all buffers (for testing/cleanup)
     */
    public void clearBuffers() {
        sensorBuffers.clear();
        processedCount.set(0);
        droppedCount.set(0);
        log.info("Cleared all data pipeline buffers");
    }

    /**
     * Pipeline statistics
     */
    public static class PipelineStats {
        public final long processedCount;
        public final long droppedCount;
        public final long totalBuffered;
        public final int activeSensors;

        public PipelineStats(long processedCount, long droppedCount, long totalBuffered, int activeSensors) {
            this.processedCount = processedCount;
            this.droppedCount = droppedCount;
            this.totalBuffered = totalBuffered;
            this.activeSensors = activeSensors;
        }
    }
}