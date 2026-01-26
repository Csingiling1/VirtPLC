package com.virtplc.service;

import java.util.Map;

/**
 * Interface for AI service operations.
 * Follows Interface Segregation Principle by defining specific AI operations.
 */
public interface AIServiceOperations {

    /**
     * Sends a chat message to the AI service.
     * 
     * @param message The message to send
     * @param context Additional context for the conversation
     * @param model   The AI model to use ('ollama' or 'claude')
     * @return The AI response
     */
    Map<String, Object> chat(String message, String context, String model);

    /**
     * Checks if the AI service is available.
     * 
     * @return true if the service is available, false otherwise
     */
    boolean isServiceAvailable();
}