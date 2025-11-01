package com.virtplc.api;

import com.virtplc.model.SimulatorDevice;
import com.virtplc.model.SignalConfig;
import com.virtplc.model.User;
import com.virtplc.service.SimulatorService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * REST API for simulator device management
 */
@RestController
@RequestMapping("/api/simulator")
@RequiredArgsConstructor
@Slf4j
public class SimulatorController {

    private final SimulatorService simulatorService;

    /**
     * Get all devices
     */
    @GetMapping("/devices")
    public ResponseEntity<List<SimulatorDevice>> getAllDevices() {
        List<SimulatorDevice> devices = simulatorService.getAllDevices();
        return ResponseEntity.ok(devices);
    }

    /**
     * Get device by ID
     */
    @GetMapping("/devices/{deviceId}")
    public ResponseEntity<SimulatorDevice> getDevice(@PathVariable String deviceId) {
        Optional<SimulatorDevice> device = simulatorService.getDevice(deviceId);
        return device.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Create new device
     */
    @PostMapping("/devices")
    public ResponseEntity<SimulatorDevice> createDevice(@RequestBody SimulatorDevice device) {
        Optional<SimulatorDevice> created = simulatorService.createDevice(device);
        return created.map(ResponseEntity::ok)
                .orElse(ResponseEntity.badRequest().build());
    }

    /**
     * Update device
     */
    @PutMapping("/devices/{deviceId}")
    public ResponseEntity<SimulatorDevice> updateDevice(
            @PathVariable String deviceId,
            @RequestBody Map<String, Object> updates) {
        Optional<SimulatorDevice> updated = simulatorService.updateDevice(deviceId, updates);
        return updated.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Delete device
     */
    @DeleteMapping("/devices/{deviceId}")
    public ResponseEntity<Void> deleteDevice(@PathVariable String deviceId) {
        boolean deleted = simulatorService.deleteDevice(deviceId);
        return deleted ? ResponseEntity.noContent().build()
                : ResponseEntity.notFound().build();
    }

    /**
     * Get signal value
     */
    @GetMapping("/devices/{deviceId}/signals/{signalName}")
    public ResponseEntity<Map<String, Object>> getSignalValue(
            @PathVariable String deviceId,
            @PathVariable String signalName) {
        Optional<Double> value = simulatorService.getSignalValue(deviceId, signalName);
        if (value.isPresent()) {
            Map<String, Object> response = Map.of(
                    "deviceId", deviceId,
                    "signalName", signalName,
                    "value", value.get());
            return ResponseEntity.ok(response);
        }
        return ResponseEntity.notFound().build();
    }

    /**
     * Set signal value
     */
    @PutMapping("/devices/{deviceId}/signals/{signalName}")
    public ResponseEntity<Void> setSignalValue(
            @PathVariable String deviceId,
            @PathVariable String signalName,
            @RequestBody Map<String, Double> payload) {
        Double value = payload.get("value");
        if (value == null) {
            return ResponseEntity.badRequest().build();
        }

        boolean success = simulatorService.setSignalValue(deviceId, signalName, value);
        return success ? ResponseEntity.ok().build()
                : ResponseEntity.notFound().build();
    }

    /**
     * Add signal to device
     */
    @PostMapping("/devices/{deviceId}/signals")
    public ResponseEntity<Void> addSignal(
            @PathVariable String deviceId,
            @RequestBody SignalConfig signal) {
        boolean success = simulatorService.addSignal(deviceId, signal);
        return success ? ResponseEntity.ok().build()
                : ResponseEntity.badRequest().build();
    }

    /**
     * Get simulation status
     */
    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getSimulationStatus() {
        Map<String, Object> status = simulatorService.getSimulationStatus();
        return ResponseEntity.ok(status);
    }

    /**
     * Trigger simulation update
     */
    @PostMapping("/update")
    public ResponseEntity<Void> updateSimulation() {
        boolean success = simulatorService.updateSimulation();
        return success ? ResponseEntity.ok().build()
                : ResponseEntity.internalServerError().build();
    }

    /**
     * Get tenants from simulator
     */
    @GetMapping("/tenants")
    public ResponseEntity<List<Map<String, Object>>> getTenants() {
        List<Map<String, Object>> tenants = simulatorService.getTenants();
        return ResponseEntity.ok(tenants);
    }

    /**
     * Get filtered tenants based on authenticated user's manufacturer
     * Non-admin users only see their manufacturer's data
     */
    @GetMapping("/tenants/my-data")
    public ResponseEntity<List<Map<String, Object>>> getMyTenantData() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        
        if (authentication == null || !(authentication.getPrincipal() instanceof User)) {
            return ResponseEntity.status(401).build();
        }

        User user = (User) authentication.getPrincipal();
        List<Map<String, Object>> tenants = simulatorService.getTenants();
        
        // ADMIN sees everything
        if (user.getRole() == User.Role.ADMIN) {
            return ResponseEntity.ok(tenants);
        }
        
        // Non-admin users only see their manufacturer's data
        if (user.getManufacturer() != null) {
            String userManufacturerId = user.getManufacturer().getManufacturerId();
            List<Map<String, Object>> filteredTenants = simulatorService.filterTenantsByManufacturer(
                tenants, userManufacturerId);
            return ResponseEntity.ok(filteredTenants);
        }
        
        // User has no manufacturer assigned - return empty
        return ResponseEntity.ok(List.of());
    }
}
