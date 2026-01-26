package com.virtplc.service;

import java.util.Map;

/**
 * Interface for AI service HTTP client operations.
 * Follows Dependency Inversion Principle by abstracting HTTP communication.
 */
public interface AIHttpClient {

    /**
     * Sends a POST request to the AI service.
     * 
     * @param url         The endpoint URL
     * @param requestBody The request payload
     * @return The response from the AI service
     * @throws AICommunicationException if the request fails
     */
    Map<String, Object> post(String url, Map<String, String> requestBody) throws AICommunicationException;

    /**
     * Checks if the AI service is reachable.
     * 
     * @param url The service URL to check
     * @return true if reachable, false otherwise
     */
    boolean isServiceReachable(String url);

    /**
     * Custom exception for AI communication errors.
     */
    class AICommunicationException extends Exception {
        public AICommunicationException(String message) {
            super(message);
        }

        public AICommunicationException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}