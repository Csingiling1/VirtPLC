package com.virtplc.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.RestClientException;

import java.util.HashMap;
import java.util.Map;

/**
 * Implementation of AI HTTP client using Spring RestTemplate.
 * Handles all HTTP communication with the AI service.
 */
@Slf4j
@Component
public class AIHttpClientImpl implements AIHttpClient {

    private final RestTemplate restTemplate;

    public AIHttpClientImpl(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @Override
    public Map<String, Object> post(String url, Map<String, String> requestBody) throws AICommunicationException {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, String>> entity = new HttpEntity<>(requestBody, headers);

            log.debug("Sending POST request to AI service: {}", url);

            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.POST, entity, (Class<Map<String, Object>>) (Class<?>) Map.class);

            if (response.getBody() != null) {
                log.debug("Received successful response from AI service");
                return response.getBody();
            } else {
                throw new AICommunicationException("Empty response from AI service");
            }

        } catch (RestClientException e) {
            log.error("Failed to communicate with AI service at {}: {}", url, e.getMessage());
            throw new AICommunicationException("AI service communication failed: " + e.getMessage(), e);
        } catch (Exception e) {
            log.error("Unexpected error communicating with AI service: {}", e.getMessage());
            throw new AICommunicationException("Unexpected error: " + e.getMessage(), e);
        }
    }

    @Override
    public boolean isServiceReachable(String url) {
        try {
            // Try to make a simple GET request to check availability
            String healthUrl = url.replace("/api/chat", "/health").replace("/api/chat/claude", "/health");

            HttpHeaders headers = new HttpHeaders();
            HttpEntity<Void> entity = new HttpEntity<>(headers);

            ResponseEntity<Void> response = restTemplate.exchange(
                    healthUrl, HttpMethod.GET, entity, Void.class);

            return response.getStatusCode().is2xxSuccessful();

        } catch (Exception e) {
            log.warn("AI service health check failed for {}: {}", url, e.getMessage());
            return false;
        }
    }
}