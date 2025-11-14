package com.virtplc.pipeline;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.Duration;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Backpressure handler for managing data flow in the pipeline
 */
@Slf4j
@Component
public class BackpressureHandler {

    private final AtomicLong totalProcessed = new AtomicLong(0);
    private final AtomicLong droppedMessages = new AtomicLong(0);
    private final AtomicLong backpressureEvents = new AtomicLong(0);

    private final int highWatermark = 1000; // Start backpressure at 1000 pending items
    private final Duration backpressureDelay = Duration.ofMillis(100);

    /**
     * Apply backpressure control to a data stream
     */
    public <T> Flux<T> withBackpressure(Flux<T> source) {
        return source
                .onBackpressureBuffer(highWatermark,
                        dropped -> {
                            long count = droppedMessages.addAndGet(1);
                            if (count % 100 == 0) { // Log every 100 dropped messages
                                log.warn("Backpressure: dropped {} messages total", count);
                            }
                        })
                .onBackpressureDrop(item -> {
                    backpressureEvents.incrementAndGet();
                    log.debug("Dropping item due to backpressure");
                })
                .doOnNext(item -> totalProcessed.incrementAndGet());
    }

    /**
     * Apply adaptive backpressure based on system load
     */
    public <T> Flux<T> withAdaptiveBackpressure(Flux<T> source, SystemLoadMonitor loadMonitor) {
        return source
                .flatMap(item -> {
                    if (loadMonitor.isHighLoad()) {
                        // Apply delay when system is under high load
                        backpressureEvents.incrementAndGet();
                        return Mono.just(item).delayElement(backpressureDelay);
                    } else {
                        return Mono.just(item);
                    }
                }, 1) // Sequential processing when backpressure is applied
                .doOnNext(item -> totalProcessed.incrementAndGet());
    }

    /**
     * Get backpressure statistics
     */
    public BackpressureStats getStats() {
        return new BackpressureStats(
                totalProcessed.get(),
                droppedMessages.get(),
                backpressureEvents.get());
    }

    /**
     * Reset statistics
     */
    public void resetStats() {
        totalProcessed.set(0);
        droppedMessages.set(0);
        backpressureEvents.set(0);
        log.info("Reset backpressure statistics");
    }

    /**
     * System load monitor interface
     */
    public interface SystemLoadMonitor {
        boolean isHighLoad();

        double getCurrentLoad();
    }

    /**
     * Backpressure statistics
     */
    public static class BackpressureStats {
        public final long totalProcessed;
        public final long droppedMessages;
        public final long backpressureEvents;

        public BackpressureStats(long totalProcessed, long droppedMessages, long backpressureEvents) {
            this.totalProcessed = totalProcessed;
            this.droppedMessages = droppedMessages;
            this.backpressureEvents = backpressureEvents;
        }

        public double getDropRate() {
            long total = totalProcessed + droppedMessages;
            return total > 0 ? (double) droppedMessages / total : 0.0;
        }
    }
}