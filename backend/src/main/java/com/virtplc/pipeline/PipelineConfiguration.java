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
    public SystemLoadMonitor systemLoadMonitor() {
        return new SimpleSystemLoadMonitor();
    }

    /**
     * Simple system load monitor based on JVM metrics
     */
    public interface SystemLoadMonitor {
        boolean isHighLoad();

        double getCurrentLoad();
    }

    /**
     * Simple system load monitor based on JVM metrics
     */
    public static class SimpleSystemLoadMonitor implements SystemLoadMonitor {

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
    public PipelineHealthCheck pipelineHealthCheck(DataPipelineService dataPipeline) {
        return new PipelineHealthCheck(dataPipeline);
    }

    /**
     * Pipeline health monitoring
     */
    public static class PipelineHealthCheck {

        private final DataPipelineService dataPipeline;

        public PipelineHealthCheck(DataPipelineService dataPipeline) {
            this.dataPipeline = dataPipeline;
        }

        public boolean isHealthy() {
            // Simplified health check - just ensure the service is available
            return dataPipeline != null;
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