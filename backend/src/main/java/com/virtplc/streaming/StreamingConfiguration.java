package com.virtplc.streaming;

import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import reactor.core.scheduler.Scheduler;
import reactor.core.scheduler.Schedulers;

import java.util.concurrent.Executors;

/**
 * Configuration for reactive streaming components
 */
@Configuration
@Slf4j
public class StreamingConfiguration {

    /**
     * Dedicated scheduler for data processing
     */
    @Bean("dataProcessingScheduler")
    public Scheduler dataProcessingScheduler() {
        int threadCount = Math.max(2, Runtime.getRuntime().availableProcessors() / 2);
        log.info("Creating data processing scheduler with {} threads", threadCount);

        return Schedulers.fromExecutor(
                Executors.newFixedThreadPool(threadCount, r -> {
                    Thread t = new Thread(r, "data-processing");
                    t.setDaemon(true);
                    return t;
                }));
    }

    /**
     * Dedicated scheduler for I/O operations
     */
    @Bean("ioScheduler")
    public Scheduler ioScheduler() {
        int threadCount = Math.max(4, Runtime.getRuntime().availableProcessors());
        log.info("Creating I/O scheduler with {} threads", threadCount);

        return Schedulers.fromExecutor(
                Executors.newFixedThreadPool(threadCount, r -> {
                    Thread t = new Thread(r, "streaming-io");
                    t.setDaemon(true);
                    return t;
                }));
    }

    /**
     * Scheduler for periodic tasks
     */
    @Bean("periodicScheduler")
    public Scheduler periodicScheduler() {
        log.info("Creating periodic scheduler with 2 threads");

        return Schedulers.fromExecutor(
                Executors.newScheduledThreadPool(2, r -> {
                    Thread t = new Thread(r, "streaming-periodic");
                    t.setDaemon(true);
                    return t;
                }));
    }
}