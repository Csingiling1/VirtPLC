package com.virtplc.service;

import com.virtplc.mcp.TimescaleMCPServer;
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
 * Service for managing simulator devices via MCP (database) and simulator
 * control
 */
@Service
@Slf4j
public class SimulatorService {

    private final TimescaleMCPServer mcpServer;
    private final RestTemplate restTemplate;
    private final String simulatorBaseUrl;

    public SimulatorService(
            TimescaleMCPServer mcpServer,
            RestTemplate restTemplate,
            @Value("${simulator.base-url:http://localhost:5000}") String simulatorBaseUrl) {
        this.mcpServer = mcpServer;
        this.restTemplate = restTemplate;
        this.simulatorBaseUrl = simulatorBaseUrl;
    }

    /**
     * Get all devices (PLCs) from database via MCP
     */
    public List<SimulatorDevice> getAllDevices() {
        try {
            List<Map<String, Object>> plcs = mcpServer.getAllPLCs();
            return plcs.stream().map(this::mapToSimulatorDevice).toList();
        } catch (Exception e) {
            log.error("Failed to fetch devices from MCP: {}", e.getMessage());
            return Collections.emptyList();
        }
    }

    /**
     * Get device by ID from database via MCP
     */
    public Optional<SimulatorDevice> getDevice(String deviceId) {
        try {
            List<Map<String, Object>> plcs = mcpServer.getAllPLCs();
            return plcs.stream()
                    .filter(plc -> deviceId.equals(plc.get("plc_id")))
                    .findFirst()
                    .map(this::mapToSimulatorDevice);
        } catch (Exception e) {
            log.error("Failed to fetch device from MCP: {}", e.getMessage());
            return Optional.empty();
        }
    }

    /**
     * Get tenants from simulator (via simulator API)
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
     * Update device (via simulator API)
     */
    public Optional<SimulatorDevice> updateDevice(String deviceId, Map<String, Object> updates) {
        try {
            String url = simulatorBaseUrl + "/devices/" + deviceId;
            restTemplate.put(url, updates);
            return getDevice(deviceId);
        } catch (RestClientException e) {
            log.error("Failed to update device {}: {}", deviceId, e.getMessage());
            return Optional.empty();
        }
    }

    /**
     * Delete device (via simulator API)
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
     * Get signal value (via simulator API)
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
     * Set signal value (via simulator API)
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
     * Add signal to device (via simulator API)
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
     * Get simulation status (via simulator API)
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
     * Trigger simulation update (via simulator API)
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
     * Get all signals (sensors) from database via MCP
     */
    public List<Map<String, Object>> getAllSignals() {
        try {
            List<Map<String, Object>> sensors = mcpServer.getAllSensors();
            return sensors.stream().map(this::mapToSignalConfig).toList();
        } catch (Exception e) {
            log.error("Failed to fetch signals from MCP: {}", e.getMessage());
            return Collections.emptyList();
        }
    }

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
     * Map database PLC record to SimulatorDevice
     */
    private SimulatorDevice mapToSimulatorDevice(Map<String, Object> plcRecord) {
        return SimulatorDevice.builder()
                .id((String) plcRecord.get("plc_id"))
                .name((String) plcRecord.get("name"))
                .deviceType("PLC")
                .isActive(true)
                .signals(Collections.emptyList())
                .build();
    }

    /**
     * Map database sensor record to signal config map
     */
    private Map<String, Object> mapToSignalConfig(Map<String, Object> sensorRecord) {
        Map<String, Object> signal = new HashMap<>();
        signal.put("id", sensorRecord.get("sensor_id"));
        signal.put("name", sensorRecord.get("name"));
        signal.put("deviceId", sensorRecord.get("plc_id"));
        signal.put("type", "sensor");
        signal.put("unit", sensorRecord.get("unit"));
        signal.put("value", sensorRecord.get("signal_value"));
        return signal;
    }
}
