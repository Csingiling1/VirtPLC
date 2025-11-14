package com.virtplc.alerting;

import com.virtplc.logging.StructuredLogger;
import com.virtplc.metrics.VirtPlcMetricsService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Alerting service for VirtPLC application
 * Monitors metrics and health status, sends alerts when thresholds are exceeded
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AlertingService {

    private final VirtPlcMetricsService metricsService;
    private final StructuredLogger structuredLogger;

    // Alert thresholds
    @Value("${virtplc.alerting.websocket.max-connections:100}")
    private int maxWebSocketConnections;

    @Value("${virtplc.alerting.pipeline.max-backpressure:1000}")
    private long maxBackpressureEvents;

    @Value("${virtplc.alerting.memory.warning-percent:85}")
    private double memoryWarningPercent;

    @Value("${virtplc.alerting.memory.critical-percent:95}")
    private double memoryCriticalPercent;

    // Alert tracking
    private final Map<String, AlertState> activeAlerts = new ConcurrentHashMap<>();
    private final AtomicInteger alertCounter = new AtomicInteger(0);

    /**
     * Scheduled alert checking - runs every 30 seconds
     */
    @Scheduled(fixedRate = 30000)
    public void checkAlerts() {
        checkWebSocketConnections();
        checkDataPipelineHealth();
        checkSystemResources();
        checkErrorRates();
    }

    /**
     * Check WebSocket connection limits
     */
    private void checkWebSocketConnections() {
        int activeConnections = metricsService.getActiveWebSocketConnections();

        if (activeConnections > maxWebSocketConnections) {
            String alertId = "websocket-high-connections";
            String message = String.format("High WebSocket connections: %d (threshold: %d)",
                    activeConnections, maxWebSocketConnections);

            if (!isAlertActive(alertId)) {
                createAlert(alertId, "WARNING", "WebSocket", message);
            }
        } else {
            clearAlert("websocket-high-connections");
        }
    }

    /**
     * Check data pipeline backpressure
     */
    private void checkDataPipelineHealth() {
        long backpressureEvents = metricsService.getDataPipelineBackpressureEvents();

        if (backpressureEvents > maxBackpressureEvents) {
            String alertId = "pipeline-high-backpressure";
            String message = String.format("High data pipeline backpressure: %d events (threshold: %d)",
                    backpressureEvents, maxBackpressureEvents);

            if (!isAlertActive(alertId)) {
                createAlert(alertId, "CRITICAL", "Data Pipeline", message);
            }
        } else {
            clearAlert("pipeline-high-backpressure");
        }
    }

    /**
     * Check system resource usage
     */
    private void checkSystemResources() {
        Runtime runtime = Runtime.getRuntime();
        long totalMemory = runtime.totalMemory();
        long freeMemory = runtime.freeMemory();
        long usedMemory = totalMemory - freeMemory;
        double memoryUsagePercent = ((double) usedMemory / totalMemory) * 100;

        if (memoryUsagePercent > memoryCriticalPercent) {
            String alertId = "memory-critical";
            String message = String.format("Critical memory usage: %.2f%% (threshold: %.2f%%)",
                    memoryUsagePercent, memoryCriticalPercent);

            if (!isAlertActive(alertId)) {
                createAlert(alertId, "CRITICAL", "System", message);
            }
        } else if (memoryUsagePercent > memoryWarningPercent) {
            String alertId = "memory-warning";
            String message = String.format("High memory usage: %.2f%% (threshold: %.2f%%)",
                    memoryUsagePercent, memoryWarningPercent);

            if (!isAlertActive(alertId)) {
                createAlert(alertId, "WARNING", "System", message);
            }
        } else {
            clearAlert("memory-critical");
            clearAlert("memory-warning");
        }
    }

    /**
     * Check error rates (placeholder for future implementation)
     */
    private void checkErrorRates() {
        // This would check error rates from metrics
        // For now, it's a placeholder
    }

    /**
     * Create a new alert
     */
    public void createAlert(String alertId, String severity, String component, String message) {
        AlertState alert = new AlertState(alertId, severity, component, message, LocalDateTime.now());
        activeAlerts.put(alertId, alert);
        alertCounter.incrementAndGet();

        structuredLogger.logAlertTriggered(alertId, severity, message);

        // Send notification (placeholder for actual notification system)
        sendNotification(alert);

        log.warn("Alert created: {} [{}] - {}", alertId, severity, message);
    }

    /**
     * Clear an active alert
     */
    public void clearAlert(String alertId) {
        AlertState alert = activeAlerts.remove(alertId);
        if (alert != null) {
            structuredLogger.logAlertTriggered(alertId + "-resolved", "INFO",
                    "Alert resolved: " + alert.getMessage());
            log.info("Alert resolved: {}", alertId);
        }
    }

    /**
     * Check if an alert is currently active
     */
    public boolean isAlertActive(String alertId) {
        return activeAlerts.containsKey(alertId);
    }

    /**
     * Get all active alerts
     */
    public Map<String, AlertState> getActiveAlerts() {
        return new ConcurrentHashMap<>(activeAlerts);
    }

    /**
     * Get alert statistics
     */
    public AlertStatistics getAlertStatistics() {
        long criticalCount = activeAlerts.values().stream()
                .mapToLong(alert -> "CRITICAL".equals(alert.getSeverity()) ? 1 : 0)
                .sum();

        long warningCount = activeAlerts.values().stream()
                .mapToLong(alert -> "WARNING".equals(alert.getSeverity()) ? 1 : 0)
                .sum();

        return new AlertStatistics(
                activeAlerts.size(),
                criticalCount,
                warningCount,
                alertCounter.get());
    }

    /**
     * Send notification (placeholder for actual implementation)
     */
    private void sendNotification(AlertState alert) {
        // Placeholder for notification implementation
        // Could integrate with:
        // - Email
        // - Slack
        // - Teams
        // - PagerDuty
        // - SMS
        // - etc.

        log.info("Notification sent for alert: {} [{}]", alert.getAlertId(), alert.getSeverity());
    }

    /**
     * Manual alert creation for custom alerts
     */
    public void createCustomAlert(String alertId, String severity, String component,
            String message, Map<String, Object> context) {
        String enhancedMessage = message;
        if (context != null && !context.isEmpty()) {
            enhancedMessage += " Context: " + context.toString();
        }
        createAlert(alertId, severity, component, enhancedMessage);
    }

    /**
     * Alert state class
     */
    public static class AlertState {
        private final String alertId;
        private final String severity;
        private final String component;
        private final String message;
        private final LocalDateTime createdAt;

        public AlertState(String alertId, String severity, String component, String message, LocalDateTime createdAt) {
            this.alertId = alertId;
            this.severity = severity;
            this.component = component;
            this.message = message;
            this.createdAt = createdAt;
        }

        // Getters
        public String getAlertId() {
            return alertId;
        }

        public String getSeverity() {
            return severity;
        }

        public String getComponent() {
            return component;
        }

        public String getMessage() {
            return message;
        }

        public LocalDateTime getCreatedAt() {
            return createdAt;
        }
    }

    /**
     * Alert statistics class
     */
    public static class AlertStatistics {
        private final long activeAlerts;
        private final long criticalAlerts;
        private final long warningAlerts;
        private final long totalAlertsCreated;

        public AlertStatistics(long activeAlerts, long criticalAlerts, long warningAlerts, long totalAlertsCreated) {
            this.activeAlerts = activeAlerts;
            this.criticalAlerts = criticalAlerts;
            this.warningAlerts = warningAlerts;
            this.totalAlertsCreated = totalAlertsCreated;
        }

        // Getters
        public long getActiveAlerts() {
            return activeAlerts;
        }

        public long getCriticalAlerts() {
            return criticalAlerts;
        }

        public long getWarningAlerts() {
            return warningAlerts;
        }

        public long getTotalAlertsCreated() {
            return totalAlertsCreated;
        }
    }
}