package com.virtplc.service;

import com.virtplc.model.SimulatorDevice;
import com.virtplc.model.SignalConfig;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.RestClientException;

import java.util.*;

/**
 * Service for managing simulator devices via REST API
 */
@Service
@Slf4j
public class SimulatorService {

    private final RestTemplate restTemplate;
    private final String simulatorBaseUrl;

    public SimulatorService(
            RestTemplate restTemplate,
            @Value("${simulator.base-url:http://localhost:5000}") String simulatorBaseUrl) {
        this.restTemplate = restTemplate;
        this.simulatorBaseUrl = simulatorBaseUrl;
    }

    /**
     * Get all devices from simulator
     */
    public List<SimulatorDevice> getAllDevices() {
        try {
            String url = simulatorBaseUrl + "/devices";
            ResponseEntity<SimulatorDevice[]> response = restTemplate.getForEntity(url, SimulatorDevice[].class);
            return Arrays.asList(Objects.requireNonNull(response.getBody()));
        } catch (RestClientException e) {
            log.error("Failed to fetch devices from simulator: {}", e.getMessage());
            return Collections.emptyList();
        }
    }

    /**
     * Get device by ID
     */
    public Optional<SimulatorDevice> getDevice(String deviceId) {
        try {
            String url = simulatorBaseUrl + "/devices/" + deviceId;
            ResponseEntity<SimulatorDevice> response = restTemplate.getForEntity(url, SimulatorDevice.class);
            return Optional.ofNullable(response.getBody());
        } catch (RestClientException e) {
            log.error("Failed to fetch device {}: {}", deviceId, e.getMessage());
            return Optional.empty();
        }
    }

    /**
     * Create new device
     */
    public Optional<SimulatorDevice> createDevice(SimulatorDevice device) {
        try {
            String url = simulatorBaseUrl + "/devices";
            ResponseEntity<SimulatorDevice> response = restTemplate.postForEntity(url, device, SimulatorDevice.class);
            log.info("Created device: {}", device.getName());
            return Optional.ofNullable(response.getBody());
        } catch (RestClientException e) {
            log.error("Failed to create device {}: {}", device.getName(), e.getMessage());
            return Optional.empty();
        }
    }

    /**
     * Update device
     */
    public Optional<SimulatorDevice> updateDevice(String deviceId, Map<String, Object> updates) {
        try {
            String url = simulatorBaseUrl + "/devices/" + deviceId;
            // Note: In a real implementation, you'd use PATCH or PUT
            // For now, we'll simulate with POST to update endpoint
            restTemplate.put(url, updates);
            return getDevice(deviceId);
        } catch (RestClientException e) {
            log.error("Failed to update device {}: {}", deviceId, e.getMessage());
            return Optional.empty();
        }
    }

    /**
     * Delete device
     */
    public boolean deleteDevice(String deviceId) {
        try {
            String url = simulatorBaseUrl + "/devices/" + deviceId;
            restTemplate.delete(url);
            log.info("Deleted device: {}", deviceId);
            return true;
        } catch (RestClientException e) {
            log.error("Failed to delete device {}: {}", deviceId, e.getMessage());
            return false;
        }
    }

    /**
     * Get signal value
     */
    @SuppressWarnings("unchecked")
    public Optional<Double> getSignalValue(String deviceId, String signalName) {
        try {
            String url = simulatorBaseUrl + "/devices/" + deviceId + "/signals/" + signalName;
            ResponseEntity<Map<String, Object>> response = restTemplate.getForEntity(url,
                    (Class<Map<String, Object>>) (Class<?>) Map.class);
            Map<String, Object> body = response.getBody();
            if (body != null && body.containsKey("value")) {
                return Optional.ofNullable((Double) body.get("value"));
            }
            return Optional.empty();
        } catch (RestClientException e) {
            log.error("Failed to get signal value {}/{}: {}", deviceId, signalName, e.getMessage());
            return Optional.empty();
        }
    }

    /**
     * Set signal value
     */
    public boolean setSignalValue(String deviceId, String signalName, Double value) {
        try {
            String url = simulatorBaseUrl + "/devices/" + deviceId + "/signals/" + signalName;
            Map<String, Object> payload = Collections.singletonMap("value", value);
            restTemplate.put(url, payload);
            return true;
        } catch (RestClientException e) {
            log.error("Failed to set signal value {}/{}: {}", deviceId, signalName, e.getMessage());
            return false;
        }
    }

    /**
     * Add signal to device
     */
    public boolean addSignal(String deviceId, SignalConfig signal) {
        try {
            String url = simulatorBaseUrl + "/devices/" + deviceId + "/signals";
            restTemplate.postForEntity(url, signal, Void.class);
            log.info("Added signal {} to device {}", signal.getName(), deviceId);
            return true;
        } catch (RestClientException e) {
            log.error("Failed to add signal {} to device {}: {}", signal.getName(), deviceId, e.getMessage());
            return false;
        }
    }

    /**
     * Get simulation status
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getSimulationStatus() {
        try {
            String url = simulatorBaseUrl + "/simulation/status";
            ResponseEntity<Map<String, Object>> response = restTemplate.getForEntity(url,
                    (Class<Map<String, Object>>) (Class<?>) Map.class);
            return response.getBody() != null ? response.getBody() : Collections.emptyMap();
        } catch (RestClientException e) {
            log.error("Failed to get simulation status: {}", e.getMessage());
            return Collections.singletonMap("error", "Simulator not available");
        }
    }

    /**
     * Trigger simulation update
     */
    public boolean updateSimulation() {
        try {
            String url = simulatorBaseUrl + "/simulation/update";
            restTemplate.postForEntity(url, null, Void.class);
            return true;
        } catch (RestClientException e) {
            log.error("Failed to update simulation: {}", e.getMessage());
            return false;
        }
    }

    /**
     * Get tenants from simulator
     */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getTenants() {
        try {
            String url = simulatorBaseUrl + "/tenants";
            ResponseEntity<List<Map<String, Object>>> response = restTemplate.getForEntity(url,
                    (Class<List<Map<String, Object>>>) (Class<?>) List.class);
            return response.getBody() != null ? response.getBody() : Collections.emptyList();
        } catch (RestClientException e) {
            log.error("Failed to get tenants from simulator: {}", e.getMessage());
            return Collections.emptyList();
        }
    }

    /**
     * Filter tenants by manufacturer ID
     * Filters the tenant hierarchy to only include the specified manufacturer and
     * its factories/PLCs/sensors
     */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> filterTenantsByManufacturer(
            List<Map<String, Object>> tenants,
            String manufacturerId) {

        return tenants.stream()
                .map(tenant -> {
                    Map<String, Object> filteredTenant = new java.util.HashMap<>(tenant);
                    List<Map<String, Object>> manufacturers = (List<Map<String, Object>>) tenant.get("manufacturers");

                    if (manufacturers != null) {
                        List<Map<String, Object>> filteredManufacturers = manufacturers.stream()
                                .filter(m -> manufacturerId.equals(m.get("id")))
                                .collect(java.util.stream.Collectors.toList());

                        filteredTenant.put("manufacturers", filteredManufacturers);
                    }

                    return filteredTenant;
                })
                .filter(tenant -> {
                    List<?> manufacturers = (List<?>) tenant.get("manufacturers");
                    return manufacturers != null && !manufacturers.isEmpty();
                })
                .collect(java.util.stream.Collectors.toList());
    }

    /**
     * Get all signals from all devices
     */
    public List<Map<String, Object>> getAllSignals() {
        List<SimulatorDevice> devices = getAllDevices();
        List<Map<String, Object>> allSignals = new ArrayList<>();

        for (SimulatorDevice device : devices) {
            if (device.getSignals() != null) {
                for (SignalConfig signal : device.getSignals()) {
                    Map<String, Object> signalMap = new HashMap<>();
                    signalMap.put("id", device.getId() + "-" + signal.getName());
                    signalMap.put("name", signal.getName());
                    signalMap.put("deviceId", device.getId());
                    signalMap.put("type", signal.getGenerator()); // or some type
                    signalMap.put("unit", signal.getUnit());
                    signalMap.put("value", signal.getValue());
                    allSignals.add(signalMap);
                }
            }
        }

        return allSignals;
    }
}
