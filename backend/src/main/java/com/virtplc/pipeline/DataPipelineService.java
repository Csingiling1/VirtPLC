package com.virtplc.pipeline;

import com.virtplc.grpc.GrpcDtos.SensorData;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

import java.time.Duration;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Real-time data pipeline with buffering and backpressure handling
 */
@Slf4j
@Service
public class DataPipelineService {

    private final ConcurrentHashMap<String, ConcurrentLinkedQueue<SensorData>> sensorBuffers = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, AtomicLong> bufferSizes = new ConcurrentHashMap<>();
    private final int maxBufferSize = 10000; // Maximum buffer size per sensor
    private final int batchSize = 100; // Process in batches of 100
    private final Duration bufferTimeout = Duration.ofMillis(100); // Buffer timeout

    /**
     * Ingest sensor data into the pipeline with backpressure
     */
    public Mono<Void> ingestSensorData(SensorData data) {
        return Mono.<Void>fromRunnable(() -> {
            String sensorId = data.getSensorId();

            // Get or create buffer for this sensor
            ConcurrentLinkedQueue<SensorData> buffer = sensorBuffers.computeIfAbsent(sensorId,
                    k -> new ConcurrentLinkedQueue<>());
            AtomicLong currentSize = bufferSizes.computeIfAbsent(sensorId, k -> new AtomicLong(0));

            // Check buffer size limit with backpressure
            if (currentSize.get() >= maxBufferSize) {
                log.warn("Buffer full for sensor {}, applying backpressure", sensorId);
                // In a real implementation, you might signal backpressure to the source
                // For now, we'll drop the oldest data to make room
                buffer.poll(); // Remove oldest
                currentSize.decrementAndGet();
            }

            // Add data to buffer
            buffer.offer(data);
            long newSize = currentSize.incrementAndGet();

            if (newSize % 1000 == 0) { // Log every 1000 messages
                log.debug("Buffer size for sensor {}: {}", sensorId, newSize);
            }
        })
                .subscribeOn(Schedulers.boundedElastic());
    }

    /**
     * Get buffered data stream for a sensor with batching
     */
    public Flux<SensorData> getBufferedSensorData(String sensorId) {
        return Flux.<SensorData>create(sink -> {
            ConcurrentLinkedQueue<SensorData> buffer = sensorBuffers.get(sensorId);

            if (buffer == null || buffer.isEmpty()) {
                sink.complete();
                return;
            }

            // Process data in batches with timeout
            Flux.interval(bufferTimeout)
                    .takeWhile(tick -> {
                        // Check if we have data to process
                        return !buffer.isEmpty();
                    })
                    .flatMap(tick -> {
                        // Collect batch of data
                        return Flux.<SensorData>create(batchSink -> {
                            int count = 0;
                            SensorData data;
                            while (count < batchSize && (data = buffer.poll()) != null) {
                                batchSink.next(data);
                                count++;
                            }
                            batchSink.complete();
                        });
                    })
                    .doOnNext(data -> {
                        AtomicLong size = bufferSizes.get(sensorId);
                        if (size != null) {
                            size.decrementAndGet();
                        }
                    })
                    .subscribe(sink::next, sink::error, sink::complete);
        })
                .subscribeOn(Schedulers.boundedElastic());
    }

    /**
     * Get aggregated data stream across all sensors
     */
    @SuppressWarnings("unchecked")
    public Flux<SensorData> getAggregatedDataStream() {
        return Flux.merge(sensorBuffers.keySet().stream()
                .map(this::getBufferedSensorData)
                .toArray(Flux[]::new))
                .subscribeOn(Schedulers.parallel());
    }

    /**
     * Get pipeline statistics
     */
    public PipelineStats getStats() {
        long totalBuffered = bufferSizes.values().stream().mapToLong(AtomicLong::get).sum();
        int activeSensors = (int) sensorBuffers.entrySet().stream()
                .filter(entry -> !entry.getValue().isEmpty())
                .count();

        return new PipelineStats(totalBuffered, activeSensors, sensorBuffers.size());
    }

    /**
     * Clear all buffers (for testing/cleanup)
     */
    public void clearBuffers() {
        sensorBuffers.clear();
        bufferSizes.clear();
        log.info("Cleared all data pipeline buffers");
    }

    /**
     * Get buffer size for a specific sensor
     */
    public long getBufferSize(String sensorId) {
        AtomicLong size = bufferSizes.get(sensorId);
        return size != null ? size.get() : 0;
    }

    /**
     * Pipeline statistics
     */
    public static class PipelineStats {
        public final long totalBufferedData;
        public final int activeSensors;
        public final int totalSensors;

        public PipelineStats(long totalBufferedData, int activeSensors, int totalSensors) {
            this.totalBufferedData = totalBufferedData;
            this.activeSensors = activeSensors;
            this.totalSensors = totalSensors;
        }
    }
}