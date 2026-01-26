package com.virtplc.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Map;

/**
 * Service for AI operations with SOLID principles:
 * - Single Responsibility: Only orchestrates AI operations
 * - Open/Closed: Extensible through dependency injection
 * - Liskov Substitution: Implements AIServiceOperations interface
 * - Interface Segregation: Uses focused interfaces
 * - Dependency Inversion: Depends on abstractions, not concretions
 */
@Slf4j
@Service
public class AIService implements AIServiceOperations {

    private final AIModelRouter modelRouter;
    private final AIHttpClient httpClient;

    public AIService(AIModelRouter modelRouter, AIHttpClient httpClient) {
        this.modelRouter = modelRouter;
        this.httpClient = httpClient;
    }

    @Override
    public Map<String, Object> chat(String message, String context, String model) {
        try {
            log.debug("Processing AI chat request for model: {}", model);

            // Validate input parameters
            validateChatParameters(message, context, model);

            // Get the appropriate endpoint for the model
            String endpointUrl = modelRouter.getEndpointForModel(model);

            // Prepare request payload
            Map<String, String> requestBody = Map.of(
                    "message", message,
                    "context", context != null ? context : "");

            // Send request to AI service
            return httpClient.post(endpointUrl, requestBody);

        } catch (AIHttpClient.AICommunicationException e) {
            log.error("AI service communication error: {}", e.getMessage());
            throw new AIServiceException("Failed to communicate with AI service: " + e.getMessage(), e);
        } catch (Exception e) {
            log.error("Unexpected error in AI chat: {}", e.getMessage());
            throw new AIServiceException("AI service error: " + e.getMessage(), e);
        }
    }

    @Override
    public boolean isServiceAvailable() {
        try {
            // Check if at least one model endpoint is reachable
            String ollamaUrl = modelRouter.getEndpointForModel("ollama");
            String claudeUrl = modelRouter.getEndpointForModel("claude");

            return httpClient.isServiceReachable(ollamaUrl) || httpClient.isServiceReachable(claudeUrl);

        } catch (Exception e) {
            log.warn("Error checking AI service availability: {}", e.getMessage());
            return false;
        }
    }

    /**
     * Analyzes data using AI models.
     */
    public Map<String, Object> analyzeData(Map<String, Object> data) {
        try {
            log.debug("Analyzing data with AI service");

            // For now, return a simple analysis result
            // This can be extended to use actual AI models
            return Map.of(
                    "analysis", "Data analysis completed",
                    "timestamp", System.currentTimeMillis(),
                    "dataPoints", data.size());

        } catch (Exception e) {
            log.error("Error analyzing data: {}", e.getMessage());
            throw new AIServiceException("Failed to analyze data: " + e.getMessage(), e);
        }
    }

    /**
     * Gets insights from AI service.
     */
    public Map<String, Object> getInsights(Long start, Long end) {
        try {
            log.debug("Getting AI insights for time range: {} to {}", start, end);

            // For now, return simple insights
            // This can be extended to use actual AI models
            return Map.of(
                    "insights", "AI-generated insights",
                    "timeRange", Map.of("start", start, "end", end),
                    "timestamp", System.currentTimeMillis());

        } catch (Exception e) {
            log.error("Error getting insights: {}", e.getMessage());
            throw new AIServiceException("Failed to get insights: " + e.getMessage(), e);
        }
    }

    /**
     * Validates chat request parameters.
     */
    private void validateChatParameters(String message, String context, String model) {
        if (message == null || message.trim().isEmpty()) {
            throw new IllegalArgumentException("Message cannot be null or empty");
        }

        if (model == null || model.trim().isEmpty()) {
            throw new IllegalArgumentException("Model cannot be null or empty");
        }

        if (!modelRouter.isModelSupported(model)) {
            throw new IllegalArgumentException("Unsupported model: " + model);
        }
    }

    /**
     * Custom exception for AI service errors.
     */
    public static class AIServiceException extends RuntimeException {
        public AIServiceException(String message) {
            super(message);
        }

        public AIServiceException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}