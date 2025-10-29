package com.virtplc.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class AIService {

    @Value("${ai.service.url:http://ai-service:3001}")
    private String aiServiceUrl;

    private final RestTemplate restTemplate;

    public AIService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> chat(String message, String context) {
        try {
            String url = aiServiceUrl + "/api/chat";

            Map<String, String> request = new HashMap<>();
            request.put("message", message);
            request.put("context", context);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, String>> entity = new HttpEntity<>(request, headers);

            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.POST, entity, (Class<Map<String, Object>>) (Class<?>) Map.class);

            if (response.getBody() != null) {
                return response.getBody();
            }

            return Map.of("response", "I apologize, but I couldn't process your request at the moment.");

        } catch (Exception e) {
            return Map.of("response",
                    "Sorry, I'm having trouble connecting to the AI service. Please try again later.");
        }
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> analyzeData(Map<String, Object> data) {
        try {
            String url = aiServiceUrl + "/api/analyze";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(data, headers);

            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.POST, entity, (Class<Map<String, Object>>) (Class<?>) Map.class);

            if (response.getBody() != null) {
                return response.getBody();
            }

            return Map.of("analysis", "No analysis available");

        } catch (Exception e) {
            return Map.of("error", "Failed to analyze data: " + e.getMessage());
        }
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> getInsights(Long start, Long end) {
        try {
            String url = aiServiceUrl + "/api/insights";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            Map<String, Object> params = new HashMap<>();
            if (start != null)
                params.put("start", start);
            if (end != null)
                params.put("end", end);

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(params, headers);

            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.POST, entity, (Class<Map<String, Object>>) (Class<?>) Map.class);

            if (response.getBody() != null) {
                return response.getBody();
            }

            return Map.of("insights", "No insights available");

        } catch (Exception e) {
            return Map.of("error", "Failed to get insights: " + e.getMessage());
        }
    }
}