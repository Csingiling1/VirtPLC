package com.virtplc.logging;

import lombok.extern.slf4j.Slf4j;
import org.slf4j.MDC;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.function.Supplier;

/**
 * Structured logging utility for VirtPLC application
 * Provides consistent logging patterns and MDC context management
 */
@Component
@Slf4j
public class StructuredLogger {

    private static final String CORRELATION_ID = "correlationId";
    private static final String USER_ID = "userId";
    private static final String SESSION_ID = "sessionId";
    private static final String OPERATION = "operation";
    private static final String COMPONENT = "component";
    private static final String DURATION_MS = "durationMs";

    /**
     * Execute operation with structured logging context
     */
    public void withContext(String operation, String component, Runnable operationRunnable) {
        try (MDC.MDCCloseable op = MDC.putCloseable(OPERATION, operation);
                MDC.MDCCloseable comp = MDC.putCloseable(COMPONENT, component)) {
            operationRunnable.run();
        }
    }

    /**
     * Execute operation with structured logging context and return result
     */
    public <T> T withContext(String operation, String component, Supplier<T> operationSupplier) {
        try (MDC.MDCCloseable op = MDC.putCloseable(OPERATION, operation);
                MDC.MDCCloseable comp = MDC.putCloseable(COMPONENT, component)) {
            return operationSupplier.get();
        }
    }

    /**
     * Set correlation ID for request tracing
     */
    public void setCorrelationId(String correlationId) {
        MDC.put(CORRELATION_ID, correlationId);
    }

    /**
     * Set user ID for audit logging
     */
    public void setUserId(String userId) {
        MDC.put(USER_ID, userId);
    }

    /**
     * Set session ID for session tracking
     */
    public void setSessionId(String sessionId) {
        MDC.put(SESSION_ID, sessionId);
    }

    /**
     * Clear all MDC context
     */
    public void clearContext() {
        MDC.clear();
    }

    /**
     * Log operation start
     */
    public void logOperationStart(String operation, Map<String, Object> context) {
        log.info("Operation started: {} with context: {}", operation, context);
    }

    /**
     * Log operation completion
     */
    public void logOperationComplete(String operation, long durationMs, Map<String, Object> context) {
        try (MDC.MDCCloseable dur = MDC.putCloseable(DURATION_MS, String.valueOf(durationMs))) {
            log.info("Operation completed: {} in {}ms with context: {}", operation, durationMs, context);
        }
    }

    /**
     * Log operation failure
     */
    public void logOperationFailed(String operation, Exception exception, Map<String, Object> context) {
        log.error("Operation failed: {} with context: {} - Error: {}", operation, context, exception.getMessage(),
                exception);
    }

    /**
     * Log security event
     */
    public void logSecurityEvent(String event, String userId, String details) {
        try (MDC.MDCCloseable user = MDC.putCloseable(USER_ID, userId)) {
            log.warn("Security event: {} - Details: {}", event, details);
        }
    }

    /**
     * Log performance warning
     */
    public void logPerformanceWarning(String operation, long durationMs, long thresholdMs) {
        try (MDC.MDCCloseable dur = MDC.putCloseable(DURATION_MS, String.valueOf(durationMs))) {
            log.warn("Performance warning: {} took {}ms (threshold: {}ms)", operation, durationMs, thresholdMs);
        }
    }

    /**
     * Log WebSocket event
     */
    public void logWebSocketEvent(String event, String sessionId, String details) {
        try (MDC.MDCCloseable sess = MDC.putCloseable(SESSION_ID, sessionId)) {
            log.info("WebSocket event: {} - Details: {}", event, details);
        }
    }

    /**
     * Log gRPC call
     */
    public void logGrpcCall(String method, String status, long durationMs) {
        try (MDC.MDCCloseable dur = MDC.putCloseable(DURATION_MS, String.valueOf(durationMs))) {
            log.info("gRPC call: {} completed with status: {} in {}ms", method, status, durationMs);
        }
    }

    /**
     * Log data pipeline event
     */
    public void logDataPipelineEvent(String event, int recordCount, String details) {
        log.info("Data pipeline event: {} - Records: {} - Details: {}", event, recordCount, details);
    }

    /**
     * Log alert triggered
     */
    public void logAlertTriggered(String alertType, String severity, String details) {
        log.warn("Alert triggered: {} [{}] - Details: {}", alertType, severity, details);
    }

    /**
     * Log system health check
     */
    public void logHealthCheck(String component, String status, String details) {
        if ("DOWN".equals(status) || "OUT_OF_SERVICE".equals(status)) {
            log.error("Health check failed: {} is {} - Details: {}", component, status, details);
        } else {
            log.debug("Health check: {} is {} - Details: {}", component, status, details);
        }
    }
}