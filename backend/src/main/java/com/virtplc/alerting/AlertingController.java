package com.virtplc.alerting;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * REST controller for alerting management
 * Provides endpoints to view and manage alerts
 */
@RestController
@RequestMapping("/api/alerts")
@RequiredArgsConstructor
public class AlertingController {

    private final AlertingService alertingService;

    /**
     * Get all active alerts
     */
    @GetMapping("/active")
    public ResponseEntity<Map<String, AlertingService.AlertState>> getActiveAlerts() {
        return ResponseEntity.ok(alertingService.getActiveAlerts());
    }

    /**
     * Get alert statistics
     */
    @GetMapping("/statistics")
    public ResponseEntity<AlertingService.AlertStatistics> getAlertStatistics() {
        return ResponseEntity.ok(alertingService.getAlertStatistics());
    }

    /**
     * Check if a specific alert is active
     */
    @GetMapping("/active/{alertId}")
    public ResponseEntity<Boolean> isAlertActive(@PathVariable String alertId) {
        return ResponseEntity.ok(alertingService.isAlertActive(alertId));
    }

    /**
     * Create a custom alert
     */
    @PostMapping("/custom")
    public ResponseEntity<Void> createCustomAlert(@RequestBody CustomAlertRequest request) {
        alertingService.createCustomAlert(
                request.getAlertId(),
                request.getSeverity(),
                request.getComponent(),
                request.getMessage(),
                request.getContext());
        return ResponseEntity.ok().build();
    }

    /**
     * Clear an active alert
     */
    @PostMapping("/clear/{alertId}")
    public ResponseEntity<Void> clearAlert(@PathVariable String alertId) {
        alertingService.clearAlert(alertId);
        return ResponseEntity.ok().build();
    }

    /**
     * Request DTO for custom alerts
     */
    public static class CustomAlertRequest {
        private String alertId;
        private String severity;
        private String component;
        private String message;
        private Map<String, Object> context;

        // Getters and setters
        public String getAlertId() {
            return alertId;
        }

        public void setAlertId(String alertId) {
            this.alertId = alertId;
        }

        public String getSeverity() {
            return severity;
        }

        public void setSeverity(String severity) {
            this.severity = severity;
        }

        public String getComponent() {
            return component;
        }

        public void setComponent(String component) {
            this.component = component;
        }

        public String getMessage() {
            return message;
        }

        public void setMessage(String message) {
            this.message = message;
        }

        public Map<String, Object> getContext() {
            return context;
        }

        public void setContext(Map<String, Object> context) {
            this.context = context;
        }
    }
}