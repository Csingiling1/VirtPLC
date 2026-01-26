package com.virtplc.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.Set;

/**
 * Implementation of AI model routing logic.
 * Follows Single Responsibility Principle by handling only routing concerns.
 */
@Slf4j
@Component
public class AIModelRouterImpl implements AIModelRouter {

    private static final Set<String> SUPPORTED_MODELS = Set.of("ollama", "claude");

    @Value("${ai.service.url:http://ai-service:3001}")
    private String baseAiServiceUrl;

    @Override
    public String getEndpointForModel(String model) {
        if (!isModelSupported(model)) {
            throw new IllegalArgumentException("Unsupported AI model: " + model);
        }

        String endpoint = switch (model.toLowerCase()) {
            case "ollama" -> "/api/chat";
            case "claude" -> "/api/chat/claude";
            default -> throw new IllegalArgumentException("Unsupported AI model: " + model);
        };

        return baseAiServiceUrl + endpoint;
    }

    @Override
    public boolean isModelSupported(String model) {
        return model != null && SUPPORTED_MODELS.contains(model.toLowerCase());
    }

    /**
     * Gets the base AI service URL.
     * 
     * @return The base URL
     */
    public String getBaseAiServiceUrl() {
        return baseAiServiceUrl;
    }
}