package com.virtplc.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

/**
 * Service for communicating with the VirtPLC Simulator via REST API.
 * Provides flexible data collection from any device structure.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class SimulatorApiService {

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    @Value("${simulator.api.url:http://simulator:8080}")
    private String simulatorApiUrl;

    /**
     * Get latest sensor data from simulator REST API.
     * This is the primary data source - more reliable than OPC-UA.
     */
    public Map<String, Object> getLatestSensorData() {
        try {
            String url = simulatorApiUrl + "/api/stream/latest";
            log.debug("Fetching data from simulator API: {}", url);
            
            String response = restTemplate.getForObject(url, String.class);
            if (response != null) {
                JsonNode jsonNode = objectMapper.readTree(response);
                Map<String, Object> data = new HashMap<>();
                
                // Convert JSON to Map for easy access
                jsonNode.fields().forEachRemaining(entry -> {
                    data.put(entry.getKey(), entry.getValue().asText());
                });
                
                log.debug("Successfully fetched data from simulator API: {} fields", data.size());
                return data;
            }
        } catch (Exception e) {
            log.error("Failed to fetch data from simulator API: {}", e.getMessage());
        }
        
        return new HashMap<>();
    }

    /**
     * Get device list from simulator API.
     */
    public JsonNode getDevices() {
        try {
            String url = simulatorApiUrl + "/devices";
            log.debug("Fetching devices from simulator API: {}", url);
            
            String response = restTemplate.getForObject(url, String.class);
            if (response != null) {
                return objectMapper.readTree(response);
            }
        } catch (Exception e) {
            log.error("Failed to fetch devices from simulator API: {}", e.getMessage());
        }
        
        return objectMapper.createObjectNode();
    }

    /**
     * Get simulation status from simulator API.
     */
    public JsonNode getSimulationStatus() {
        try {
            String url = simulatorApiUrl + "/simulation/status";
            log.debug("Fetching simulation status from simulator API: {}", url);
            
            String response = restTemplate.getForObject(url, String.class);
            if (response != null) {
                return objectMapper.readTree(response);
            }
        } catch (Exception e) {
            log.error("Failed to fetch simulation status from simulator API: {}", e.getMessage());
        }
        
        return objectMapper.createObjectNode();
    }

    /**
     * Check if simulator API is available.
     */
    public boolean isAvailable() {
        try {
            getSimulationStatus();
            return true;
        } catch (Exception e) {
            log.debug("Simulator API not available: {}", e.getMessage());
            return false;
        }
    }
}
