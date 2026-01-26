package com.virtplc.pipeline;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import reactor.core.publisher.Mono;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.core.JsonProcessingException;

import java.time.Instant;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;

/**
 * Data Pipeline Service for processing MQTT-based industrial IoT data streams.
 * Handles real-time data ingestion, validation, transformation, and routing.
 *
 * Why implement preprocessing in Spring backend even with Node-RED
 * preprocessing:
 * 1. Defense in depth: Multiple validation layers prevent corrupted data
 * 2. Backend authority: Spring backend is the system of record for data
 * integrity
 * 3. Protocol translation: Handles MQTT-to-internal format conversion
 * 4. Business logic: Applies domain-specific rules and transformations
 * 5. Monitoring: Comprehensive metrics and alerting at the application layer
 * 6. Fallback processing: Continues working if Node-RED fails
 * 7. Schema evolution: Manages data structure changes over time
 */
@Slf4j
@Service
public class DataPipelineService {

    private final ObjectMapper objectMapper;
    private final AtomicLong messagesProcessed = new AtomicLong(0);
    private final AtomicLong errorsEncountered = new AtomicLong(0);
    private final AtomicReference<Double> avgProcessingTime = new AtomicReference<>(0.0);

    // Configuration for data validation
    private static final double MAX_RPM = 5000.0;
    private static final double MIN_RPM = 0.0;
    private static final double MAX_POSITION = 10000.0;
    private static final double MIN_POSITION = -10000.0;

    @Autowired
    public DataPipelineService(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    /**
     * Process incoming MQTT data with comprehensive validation and transformation.
     * Even though Node-RED preprocesses data, the Spring backend provides:
     * - Authoritative data validation and schema enforcement
     * - Business logic application and data enrichment
     * - Comprehensive error handling and dead letter queuing
     * - Real-time analytics triggering and alerting
     * - Protocol translation and format standardization
     */
    public Mono<Void> processMqttData(String topic, String payload) {
        long startTime = System.nanoTime();

        return Mono.<Void>fromRunnable(() -> {
            try {
                log.debug("Processing MQTT data from topic: {}, payload length: {}", topic, payload.length());

                // Step 1: Parse and validate JSON structure
                JsonNode dataNode = parseAndValidateJson(payload);

                // Step 2: Apply business validation rules
                validateBusinessRules(dataNode, topic);

                // Step 3: Enrich data with metadata
                JsonNode enrichedData = enrichData(dataNode, topic);

                // Step 4: Route to appropriate downstream systems
                routeDataToStreams(topic, enrichedData);

                // Step 5: Trigger real-time analytics
                triggerRealTimeAnalytics(topic, enrichedData);

                // Update metrics
                long processingTime = System.nanoTime() - startTime;
                updateMetrics(processingTime / 1_000_000.0); // Convert to milliseconds

                messagesProcessed.incrementAndGet();
                log.debug("Successfully processed data from topic: {}", topic);

            } catch (DataValidationException e) {
                log.warn("Data validation failed for topic {}: {}", topic, e.getMessage());
                handleValidationError(topic, payload, e);
            } catch (Exception e) {
                log.error("Error processing MQTT data from topic {}: {}", topic, e.getMessage(), e);
                handleProcessingError(topic, payload, e);
            }
        });
    }

    /**
     * Parse JSON payload and validate basic structure.
     */
    private JsonNode parseAndValidateJson(String payload) throws DataValidationException {
        try {
            if (payload == null || payload.trim().isEmpty()) {
                throw new DataValidationException("Empty payload received");
            }

            JsonNode node = objectMapper.readTree(payload);

            // Validate required fields based on topic
            if (!node.has("device_id")) {
                throw new DataValidationException("Missing required field: device_id");
            }

            if (!node.has("timestamp")) {
                throw new DataValidationException("Missing required field: timestamp");
            }

            return node;

        } catch (JsonProcessingException e) {
            throw new DataValidationException("Invalid JSON format: " + e.getMessage());
        }
    }

    /**
     * Apply business-specific validation rules for industrial data.
     */
    private void validateBusinessRules(JsonNode data, String topic) throws DataValidationException {
        // Validate RPM values
        if (data.has("rpm")) {
            double rpm = data.get("rpm").asDouble();
            if (rpm < MIN_RPM || rpm > MAX_RPM) {
                throw new DataValidationException(
                        String.format("RPM value %.2f out of valid range [%.2f, %.2f]", rpm, MIN_RPM, MAX_RPM));
            }
        }

        // Validate position coordinates
        if (data.has("position_x")) {
            double posX = data.get("position_x").asDouble();
            if (posX < MIN_POSITION || posX > MAX_POSITION) {
                throw new DataValidationException(
                        String.format("Position X %.2f out of valid range [%.2f, %.2f]", posX, MIN_POSITION,
                                MAX_POSITION));
            }
        }

        if (data.has("position_y")) {
            double posY = data.get("position_y").asDouble();
            if (posY < MIN_POSITION || posY > MAX_POSITION) {
                throw new DataValidationException(
                        String.format("Position Y %.2f out of valid range [%.2f, %.2f]", posY, MIN_POSITION,
                                MAX_POSITION));
            }
        }

        // Validate timestamp is not in future (with 1 minute tolerance)
        if (data.has("timestamp")) {
            try {
                Instant dataTime = Instant.parse(data.get("timestamp").asText());
                Instant now = Instant.now();
                if (dataTime.isAfter(now.plusSeconds(60))) {
                    throw new DataValidationException("Timestamp is in the future");
                }
            } catch (Exception e) {
                throw new DataValidationException("Invalid timestamp format");
            }
        }
    }

    /**
     * Enrich data with additional metadata and derived fields.
     */
    private JsonNode enrichData(JsonNode originalData, String topic) {
        ObjectNode enriched = objectMapper.createObjectNode();
        enriched.setAll((ObjectNode) originalData);

        // Add processing metadata
        enriched.put("processed_at", Instant.now().toString());
        enriched.put("processing_layer", "spring_backend");
        enriched.put("topic", topic);

        // Calculate derived fields if possible
        if (originalData.has("position_x") && originalData.has("position_y")) {
            double x = originalData.get("position_x").asDouble();
            double y = originalData.get("position_y").asDouble();
            double distance = Math.sqrt(x * x + y * y);
            enriched.put("distance_from_origin", Math.round(distance * 100.0) / 100.0);
        }

        // Add data quality score
        int qualityScore = calculateDataQuality(originalData);
        enriched.put("data_quality_score", qualityScore);

        return enriched;
    }

    /**
     * Calculate data quality score based on completeness and validity.
     */
    private int calculateDataQuality(JsonNode data) {
        int score = 100;
        String[] requiredFields = { "device_id", "timestamp", "rpm" };

        // Deduct points for missing required fields
        for (String field : requiredFields) {
            if (!data.has(field) || data.get(field).isNull()) {
                score -= 25;
            }
        }

        // Deduct points for missing optional but valuable fields
        if (!data.has("position_x") || !data.has("position_y")) {
            score -= 10;
        }

        return Math.max(0, score);
    }

    /**
     * Route processed data to appropriate downstream systems.
     */
    private void routeDataToStreams(String topic, JsonNode data) {
        try {
            String deviceId = data.get("device_id").asText();

            // Route to TimescaleDB for time-series storage
            routeToTimescaleDB(data);

            // Route to Redis for real-time caching
            routeToRedis(data);

            // Route to analytics pipeline if high-priority data
            if (isHighPriorityData(data)) {
                routeToAnalyticsPipeline(data);
            }

            log.debug("Successfully routed data from device {} to downstream systems", deviceId);

        } catch (Exception e) {
            log.error("Failed to route data to streams: {}", e.getMessage());
            throw new RuntimeException("Data routing failed", e);
        }
    }

    /**
     * Route data to TimescaleDB for persistent time-series storage.
     */
    private void routeToTimescaleDB(JsonNode data) {
        // Implementation would integrate with TimescaleDB repository
        log.debug("Routing data to TimescaleDB for device: {}", data.get("device_id").asText());
    }

    /**
     * Route data to Redis for high-speed caching and real-time access.
     */
    private void routeToRedis(JsonNode data) {
        // Implementation would use RedisTemplate for caching
        log.debug("Caching data in Redis for device: {}", data.get("device_id").asText());
    }

    /**
     * Route high-priority data to analytics pipeline.
     */
    private void routeToAnalyticsPipeline(JsonNode data) {
        // Implementation would send to Kafka/Redis streams for complex analytics
        log.debug("Routing high-priority data to analytics pipeline for device: {}", data.get("device_id").asText());
    }

    /**
     * Determine if data should be treated as high priority.
     */
    private boolean isHighPriorityData(JsonNode data) {
        // High priority if RPM is above threshold or data quality is low
        if (data.has("rpm")) {
            double rpm = data.get("rpm").asDouble();
            if (rpm > MAX_RPM * 0.8) { // 80% of max RPM
                return true;
            }
        }

        if (data.has("data_quality_score")) {
            int quality = data.get("data_quality_score").asInt();
            if (quality < 50) { // Low quality data needs immediate attention
                return true;
            }
        }

        return false;
    }

    /**
     * Trigger real-time analytics processing based on data patterns.
     */
    private void triggerRealTimeAnalytics(String topic, JsonNode data) {
        try {
            String deviceId = data.get("device_id").asText();

            // Check for anomaly patterns
            if (detectAnomalyPattern(data)) {
                triggerAnomalyAlert(deviceId, data);
            }

            // Check for predictive maintenance triggers
            if (shouldTriggerMaintenanceAnalysis(data)) {
                triggerMaintenanceAnalysis(deviceId, data);
            }

            // Trigger real-time KPI calculations
            updateRealtimeKPIs(data);

            log.debug("Completed real-time analytics for device: {}", deviceId);

        } catch (Exception e) {
            log.error("Failed to trigger real-time analytics: {}", e.getMessage());
            // Don't throw - analytics failure shouldn't stop data processing
        }
    }

    /**
     * Simple anomaly detection based on threshold rules.
     */
    private boolean detectAnomalyPattern(JsonNode data) {
        // This would be enhanced with ML models in production
        if (data.has("rpm")) {
            double rpm = data.get("rpm").asDouble();
            // Simple threshold-based anomaly detection
            return rpm > MAX_RPM * 0.9 || rpm < MIN_RPM + 10;
        }
        return false;
    }

    /**
     * Determine if maintenance analysis should be triggered.
     */
    private boolean shouldTriggerMaintenanceAnalysis(JsonNode data) {
        // Trigger based on operating hours, vibration patterns, etc.
        // Simplified logic for demonstration
        return data.has("rpm") && data.get("rpm").asDouble() > MAX_RPM * 0.7;
    }

    /**
     * Trigger anomaly alert for monitoring systems.
     */
    private void triggerAnomalyAlert(String deviceId, JsonNode data) {
        log.warn("Anomaly detected for device {}: {}", deviceId, data.toString());
        // Implementation would send to alerting system (email, SMS, etc.)
    }

    /**
     * Trigger predictive maintenance analysis.
     */
    private void triggerMaintenanceAnalysis(String deviceId, JsonNode data) {
        log.info("Triggering maintenance analysis for device {}: {}", deviceId, data.toString());
        // Implementation would queue for ML-based maintenance prediction
    }

    /**
     * Update real-time KPIs based on incoming data.
     */
    private void updateRealtimeKPIs(JsonNode data) {
        // Implementation would update cached KPI values
        log.debug("Updating real-time KPIs for device: {}", data.get("device_id").asText());
    }

    /**
     * Handle validation errors with appropriate logging and dead letter queuing.
     */
    private void handleValidationError(String topic, String payload, DataValidationException e) {
        errorsEncountered.incrementAndGet();
        log.warn("Data validation error for topic {}: {}", topic, e.getMessage());

        // Implementation would send to dead letter queue or error topic
        // For now, just log the error details
    }

    /**
     * Handle processing errors with comprehensive error tracking.
     */
    private void handleProcessingError(String topic, String payload, Exception e) {
        errorsEncountered.incrementAndGet();
        log.error("Data processing error for topic {}: {}", topic, e.getMessage());

        // Implementation would send to error monitoring system
        // Could also implement circuit breaker pattern for downstream systems
    }

    /**
     * Update processing metrics.
     */
    private void updateMetrics(double processingTimeMs) {
        // Simple moving average calculation
        double currentAvg = avgProcessingTime.get();
        double newAvg = (currentAvg + processingTimeMs) / 2.0;
        avgProcessingTime.set(newAvg);
    }

    /**
     * Get comprehensive pipeline health metrics.
     */
    public PipelineMetrics getMetrics() {
        PipelineMetrics metrics = new PipelineMetrics();
        metrics.setMessagesProcessed(messagesProcessed.get());
        metrics.setErrorsEncountered(errorsEncountered.get());
        metrics.setAverageProcessingTime(avgProcessingTime.get());
        return metrics;
    }

    /**
     * Custom exception for data validation errors.
     */
    public static class DataValidationException extends Exception {
        public DataValidationException(String message) {
            super(message);
        }
    }

    /**
     * Pipeline metrics data class with comprehensive tracking.
     */
    public static class PipelineMetrics {
        private long messagesProcessed = 0;
        private long errorsEncountered = 0;
        private double averageProcessingTime = 0.0;
        private Instant lastUpdated = Instant.now();

        // Getters and setters
        public long getMessagesProcessed() {
            return messagesProcessed;
        }

        public void setMessagesProcessed(long messagesProcessed) {
            this.messagesProcessed = messagesProcessed;
            this.lastUpdated = Instant.now();
        }

        public long getErrorsEncountered() {
            return errorsEncountered;
        }

        public void setErrorsEncountered(long errorsEncountered) {
            this.errorsEncountered = errorsEncountered;
            this.lastUpdated = Instant.now();
        }

        public double getAverageProcessingTime() {
            return averageProcessingTime;
        }

        public void setAverageProcessingTime(double averageProcessingTime) {
            this.averageProcessingTime = averageProcessingTime;
            this.lastUpdated = Instant.now();
        }

        public Instant getLastUpdated() {
            return lastUpdated;
        }

        // Calculated metrics
        public double getErrorRate() {
            if (messagesProcessed == 0)
                return 0.0;
            return (double) errorsEncountered / messagesProcessed * 100.0;
        }

        public String getHealthStatus() {
            double errorRate = getErrorRate();
            if (errorRate > 10.0)
                return "CRITICAL";
            if (errorRate > 5.0)
                return "WARNING";
            return "HEALTHY";
        }
    }
}