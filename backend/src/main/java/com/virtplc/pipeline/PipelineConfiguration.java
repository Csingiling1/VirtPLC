package com.virtplc.pipeline;

import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Data pipeline configuration
 */
@Configuration
@Slf4j
public class PipelineConfiguration {

    /**
     * System load monitor implementation
     */
    @Bean
    public BackpressureHandler.SystemLoadMonitor systemLoadMonitor() {
        return new SimpleSystemLoadMonitor();
    }

    /**
     * Simple system load monitor based on JVM metrics
     */
    public static class SimpleSystemLoadMonitor implements BackpressureHandler.SystemLoadMonitor {

        private static final double HIGH_LOAD_THRESHOLD = 0.8; // 80% CPU or memory usage

        @Override
        public boolean isHighLoad() {
            // Simple load detection based on available memory
            Runtime runtime = Runtime.getRuntime();
            long freeMemory = runtime.freeMemory();
            long totalMemory = runtime.totalMemory();
            double memoryUsage = 1.0 - ((double) freeMemory / totalMemory);

            return memoryUsage > HIGH_LOAD_THRESHOLD;
        }

        @Override
        public double getCurrentLoad() {
            Runtime runtime = Runtime.getRuntime();
            long freeMemory = runtime.freeMemory();
            long totalMemory = runtime.totalMemory();
            return 1.0 - ((double) freeMemory / totalMemory);
        }
    }

    /**
     * Pipeline health check bean
     */
    @Bean
    public PipelineHealthCheck pipelineHealthCheck(DataPipelineService dataPipeline,
            BackpressureHandler backpressureHandler) {
        return new PipelineHealthCheck(dataPipeline, backpressureHandler);
    }

    /**
     * Pipeline health monitoring
     */
    public static class PipelineHealthCheck {

        private final DataPipelineService dataPipeline;
        private final BackpressureHandler backpressureHandler;

        public PipelineHealthCheck(DataPipelineService dataPipeline, BackpressureHandler backpressureHandler) {
            this.dataPipeline = dataPipeline;
            this.backpressureHandler = backpressureHandler;
        }

        public boolean isHealthy() {
            try {
                DataPipelineService.PipelineStats pipelineStats = dataPipeline.getStats();
                BackpressureHandler.BackpressureStats backpressureStats = backpressureHandler.getStats();

                // Check for excessive dropped messages (more than 5% drop rate)
                double dropRate = backpressureStats.getDropRate();
                if (dropRate > 0.05) {
                    log.warn("High drop rate detected: {}%", dropRate * 100);
                    return false;
                }

                // Check for excessive buffered data
                if (pipelineStats.totalBufferedData > 50000) {
                    log.warn("Excessive buffered data: {}", pipelineStats.totalBufferedData);
                    return false;
                }

                return true;
            } catch (Exception e) {
                log.error("Error checking pipeline health", e);
                return false;
            }
        }

        public String getHealthStatus() {
            if (isHealthy()) {
                return "HEALTHY";
            } else {
                return "DEGRADED";
            }
        }
    }
}