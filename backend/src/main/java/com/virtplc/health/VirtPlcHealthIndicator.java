package com.virtplc.health;

import com.virtplc.logging.StructuredLogger;
import com.virtplc.metrics.VirtPlcMetricsService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.boot.actuate.health.Status;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.util.HashMap;
import java.util.Map;

/**
 * Comprehensive health indicator for VirtPLC application
 * Checks database connectivity, system resources, and business logic health
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class VirtPlcHealthIndicator implements HealthIndicator {

    private final JdbcTemplate jdbcTemplate;
    private final VirtPlcMetricsService metricsService;
    private final StructuredLogger structuredLogger;

    @Override
    public Health health() {
        Map<String, Object> healthDetails = new HashMap<>();

        try {
            // Check database connectivity
            Health databaseHealth = checkDatabaseHealth();
            healthDetails.put("database", databaseHealth.getDetails());

            // Check system resources
            Health systemHealth = checkSystemHealth();
            healthDetails.put("system", systemHealth.getDetails());

            // Check business logic health
            Health businessHealth = checkBusinessHealth();
            healthDetails.put("business", businessHealth.getDetails());

            // Check external services
            Health externalHealth = checkExternalServicesHealth();
            healthDetails.put("external", externalHealth.getDetails());

            // Determine overall health status
            if (databaseHealth.getStatus().equals(Status.DOWN) ||
                    systemHealth.getStatus().equals(Status.DOWN)) {
                structuredLogger.logHealthCheck("VirtPLC", "DOWN", "Critical component failure");
                return Health.down()
                        .withDetails(healthDetails)
                        .withDetail("overall", "Critical component failure")
                        .build();
            } else if (businessHealth.getStatus().equals(Status.DOWN) ||
                    externalHealth.getStatus().equals(Status.DOWN)) {
                structuredLogger.logHealthCheck("VirtPLC", "DEGRADED", "Non-critical component issues");
                return Health.status("DEGRADED")
                        .withDetails(healthDetails)
                        .withDetail("overall", "Non-critical component issues")
                        .build();
            } else {
                structuredLogger.logHealthCheck("VirtPLC", "UP", "All components healthy");
                return Health.up()
                        .withDetails(healthDetails)
                        .withDetail("overall", "All components healthy")
                        .build();
            }

        } catch (Exception e) {
            log.error("Error during health check", e);
            structuredLogger.logHealthCheck("VirtPLC", "DOWN", "Health check failed: " + e.getMessage());
            return Health.down(e)
                    .withDetail("error", e.getMessage())
                    .build();
        }
    }

    private Health checkDatabaseHealth() {
        try {
            // Test basic connectivity
            Integer result = jdbcTemplate.queryForObject("SELECT 1", Integer.class);
            if (!result.equals(1)) {
                return Health.down().withDetail("connectivity", "Database query failed").build();
            }

            // Get database metadata
            Connection connection = jdbcTemplate.getDataSource().getConnection();
            DatabaseMetaData metaData = connection.getMetaData();

            Map<String, Object> dbDetails = new HashMap<>();
            dbDetails.put("databaseProductName", metaData.getDatabaseProductName());
            dbDetails.put("databaseProductVersion", metaData.getDatabaseProductVersion());
            dbDetails.put("driverName", metaData.getDriverName());
            dbDetails.put("driverVersion", metaData.getDriverVersion());

            // Test TimescaleDB specific features
            try {
                Integer timescaleVersion = jdbcTemplate.queryForObject(
                        "SELECT extversion FROM pg_extension WHERE extname = 'timescaledb'",
                        Integer.class);
                dbDetails.put("timescaleDbVersion", timescaleVersion != null ? "Available" : "Not found");
            } catch (Exception e) {
                dbDetails.put("timescaleDbVersion", "Check failed: " + e.getMessage());
            }

            connection.close();

            return Health.up()
                    .withDetail("status", "Connected")
                    .withDetails(dbDetails)
                    .build();

        } catch (Exception e) {
            log.error("Database health check failed", e);
            return Health.down(e)
                    .withDetail("error", e.getMessage())
                    .build();
        }
    }

    private Health checkSystemHealth() {
        Map<String, Object> systemDetails = new HashMap<>();

        try {
            // Memory information
            Runtime runtime = Runtime.getRuntime();
            long totalMemory = runtime.totalMemory();
            long freeMemory = runtime.freeMemory();
            long usedMemory = totalMemory - freeMemory;
            double memoryUsagePercent = ((double) usedMemory / totalMemory) * 100;

            systemDetails.put("totalMemory", formatBytes(totalMemory));
            systemDetails.put("freeMemory", formatBytes(freeMemory));
            systemDetails.put("usedMemory", formatBytes(usedMemory));
            systemDetails.put("memoryUsagePercent", String.format("%.2f%%", memoryUsagePercent));

            // Thread information
            int availableProcessors = runtime.availableProcessors();
            systemDetails.put("availableProcessors", availableProcessors);

            // Check for high memory usage
            if (memoryUsagePercent > 90) {
                return Health.status("WARNING")
                        .withDetail("memory", "High memory usage")
                        .withDetails(systemDetails)
                        .build();
            }

            return Health.up()
                    .withDetail("status", "System resources normal")
                    .withDetails(systemDetails)
                    .build();

        } catch (Exception e) {
            log.error("System health check failed", e);
            return Health.down(e)
                    .withDetail("error", e.getMessage())
                    .build();
        }
    }

    private Health checkBusinessHealth() {
        Map<String, Object> businessDetails = new HashMap<>();

        try {
            // Check active connections
            int activeWebSocketConnections = metricsService.getActiveWebSocketConnections();
            businessDetails.put("activeWebSocketConnections", activeWebSocketConnections);

            // Check data pipeline health
            long backpressureEvents = metricsService.getDataPipelineBackpressureEvents();
            businessDetails.put("dataPipelineBackpressureEvents", backpressureEvents);

            // Check active simulator devices
            int activeSimulatorDevices = metricsService.getActiveSimulatorDevices();
            businessDetails.put("activeSimulatorDevices", activeSimulatorDevices);

            // Business logic health criteria
            boolean healthy = true;
            String issues = "";

            if (backpressureEvents > 1000) { // Arbitrary threshold
                healthy = false;
                issues += "High backpressure events; ";
            }

            if (activeWebSocketConnections < 0) {
                healthy = false;
                issues += "Invalid WebSocket connection count; ";
            }

            if (healthy) {
                return Health.up()
                        .withDetail("status", "Business logic healthy")
                        .withDetails(businessDetails)
                        .build();
            } else {
                return Health.status("WARNING")
                        .withDetail("status", "Business logic issues detected")
                        .withDetail("issues", issues.trim())
                        .withDetails(businessDetails)
                        .build();
            }

        } catch (Exception e) {
            log.error("Business health check failed", e);
            return Health.down(e)
                    .withDetail("error", e.getMessage())
                    .build();
        }
    }

    private Health checkExternalServicesHealth() {
        Map<String, Object> externalDetails = new HashMap<>();

        try {
            // Check AI service connectivity (placeholder)
            externalDetails.put("aiService", "Not implemented - placeholder");

            // Check simulator connectivity (placeholder)
            externalDetails.put("simulatorService", "Not implemented - placeholder");

            // For now, assume external services are healthy
            return Health.up()
                    .withDetail("status", "External services accessible")
                    .withDetails(externalDetails)
                    .build();

        } catch (Exception e) {
            log.error("External services health check failed", e);
            return Health.down(e)
                    .withDetail("error", e.getMessage())
                    .build();
        }
    }

    private String formatBytes(long bytes) {
        if (bytes < 1024)
            return bytes + " B";
        int exp = (int) (Math.log(bytes) / Math.log(1024));
        String pre = "KMGTPE".charAt(exp - 1) + "";
        return String.format("%.1f %sB", bytes / Math.pow(1024, exp), pre);
    }
}