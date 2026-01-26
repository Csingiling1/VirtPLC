package com.virtplc.service;

/**
 * Interface for AI model routing.
 * Separates the routing logic from the service implementation.
 */
public interface AIModelRouter {

    /**
     * Routes a request to the appropriate AI model endpoint.
     * 
     * @param model The model type
     * @return The endpoint URL for the model
     */
    String getEndpointForModel(String model);

    /**
     * Validates that a model is supported.
     * 
     * @param model The model to validate
     * @return true if supported, false otherwise
     */
    boolean isModelSupported(String model);
}