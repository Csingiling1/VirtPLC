package com.virtplc.api;

import com.virtplc.model.Factory;
import com.virtplc.model.PLC;
import com.virtplc.model.Sensor;
import com.virtplc.model.Manufacturer;
import com.virtplc.model.SignalConfig;
import com.virtplc.repository.FactoryRepository;
import com.virtplc.repository.PLCRepository;
import com.virtplc.repository.SensorRepository;
import com.virtplc.repository.PlcDataRepository;
import com.virtplc.repository.ManufacturerRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class AdminController {

    private final FactoryRepository factoryRepository;
    private final PLCRepository plcRepository;
    private final SensorRepository sensorRepository;
    private final PlcDataRepository plcDataRepository;
    private final ManufacturerRepository manufacturerRepository;

    @GetMapping("/factories")
    public ResponseEntity<List<Map<String, Object>>> getFactories() {
        try {
            List<Factory> factories = factoryRepository.findAll();
            List<Map<String, Object>> factoryData = factories.stream()
                    .map(factory -> {
                        Map<String, Object> factoryMap = new HashMap<>();
                        factoryMap.put("id", factory.getId().toString());
                        factoryMap.put("factoryId", factory.getFactoryId());
                        factoryMap.put("name", factory.getName());
                        factoryMap.put("description", factory.getDescription());
                        factoryMap.put("createdAt", factory.getCreatedAt());
                        factoryMap.put("devices", new ArrayList<>()); // Keep empty for now to avoid lazy loading issues
                        return factoryMap;
                    })
                    .collect(Collectors.toList());

            return ResponseEntity.ok(factoryData);
        } catch (Exception e) {
            log.error("Error fetching factories", e);
            return ResponseEntity.internalServerError().build();
        }
    }

    @GetMapping("/devices")
    public ResponseEntity<List<Map<String, Object>>> getDevices() {
        try {
            // Get all existing PLCs
            List<PLC> allPlcs = plcRepository.findAll();
            List<Map<String, Object>> deviceData = allPlcs.stream()
                    .map(this::convertPlcToDevice)
                    .collect(Collectors.toList());

            // Discover additional devices from plc_data table
            Set<String> existingPlcIds = allPlcs.stream()
                    .map(PLC::getPlcId)
                    .collect(Collectors.toSet());

            List<Map<String, Object>> plcDataDevices = discoverDevicesFromPlcData(existingPlcIds);
            deviceData.addAll(plcDataDevices);

            // Deduplicate by id
            deviceData = deviceData.stream()
                    .collect(Collectors.toMap(d -> (String) d.get("id"), d -> d, (existing, replacement) -> existing))
                    .values()
                    .stream()
                    .collect(Collectors.toList());

            return ResponseEntity.ok(deviceData);
        } catch (Exception e) {
            log.error("Error fetching devices", e);
            return ResponseEntity.internalServerError().build();
        }
    }

    @GetMapping("/device-assignments")
    public ResponseEntity<Map<String, Object>> getDeviceAssignments() {
        try {
            // Get all factories
            List<Factory> factories = factoryRepository.findAll();

            // Get all PLCs (devices)
            List<PLC> allPlcs = plcRepository.findAll();

            // Group PLCs by factory
            Map<Long, List<PLC>> plcsByFactory = allPlcs.stream()
                    .filter(plc -> plc.getFactory() != null)
                    .collect(Collectors.groupingBy(plc -> plc.getFactory().getId()));

            // Create factory data with devices
            List<Map<String, Object>> factoryData = factories.stream()
                    .map(factory -> {
                        List<PLC> factoryPlcs = plcsByFactory.getOrDefault(factory.getId(), new ArrayList<>());
                        List<Map<String, Object>> deviceData = factoryPlcs.stream()
                                .map(this::convertPlcToDevice)
                                .collect(Collectors.toList());

                        Map<String, Object> factoryMap = new HashMap<>();
                        factoryMap.put("id", factory.getId().toString());
                        factoryMap.put("factoryId", factory.getFactoryId());
                        factoryMap.put("name", factory.getName());
                        factoryMap.put("devices", deviceData);
                        return factoryMap;
                    })
                    .collect(Collectors.toList());

            // Get orphan devices (PLCs not assigned to any factory)
            List<PLC> orphanPlcs = allPlcs.stream()
                    .filter(plc -> plc.getFactory() == null)
                    .collect(Collectors.toList());

            List<Map<String, Object>> orphanData = orphanPlcs.stream()
                    .map(this::convertPlcToDevice)
                    .collect(Collectors.toList());

            // Discover devices from plc_data table that are not already in PLC entities
            Set<String> existingPlcIds = allPlcs.stream()
                    .map(PLC::getPlcId)
                    .collect(Collectors.toSet());

            List<Map<String, Object>> plcDataDevices = discoverDevicesFromPlcData(existingPlcIds);
            orphanData.addAll(plcDataDevices);

            Map<String, Object> response = new HashMap<>();
            response.put("factories", factoryData);
            response.put("orphans", orphanData);

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Error fetching device assignments", e);
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", "Failed to fetch device assignments"));
        }
    }

    @PostMapping("/device-assignments")
    @Transactional
    public ResponseEntity<Map<String, Object>> saveDeviceAssignments(
            @RequestBody Map<String, Object> request) {
        try {
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> assignments = (List<Map<String, Object>>) request.get("assignments");

            for (Map<String, Object> assignment : assignments) {
                String deviceId = (String) assignment.get("deviceId");
                String factoryId = (String) assignment.get("factoryId");
                @SuppressWarnings("unchecked")
                List<String> signalIds = (List<String>) assignment.get("signalIds");

                // Find existing PLC
                Optional<PLC> plcOpt = plcRepository.findByPlcId(deviceId);
                PLC plc;

                if (plcOpt.isPresent()) {
                    // Update existing PLC
                    plc = plcOpt.get();
                } else {
                    // Create new PLC for discovered device
                    plc = new PLC();
                    plc.setPlcId(deviceId);
                    plc.setName(formatDeviceName(deviceId));
                    plc.setDescription("Auto-created PLC for discovered device");
                    plc.setIsActive(true);
                    plc.setCreatedAt(java.time.LocalDateTime.now());
                    plc.setUpdatedAt(java.time.LocalDateTime.now());

                    // Get the factory
                    Factory factory = factoryRepository.findById(Long.parseLong(factoryId))
                        .orElseThrow(() -> new RuntimeException("Factory not found: " + factoryId));
                    plc.setFactory(factory);

                    // Save PLC first
                    plcRepository.save(plc);

                    // Create sensors for the signals
                    if (signalIds != null) {
                        for (String signalId : signalIds) {
                            Sensor sensor = new Sensor();
                            sensor.setPlc(plc);
                            sensor.setSensorId(signalId);
                            sensor.setName(formatSignalName(signalId));
                            sensor.setIsActive(true);
                            sensor.setCreatedAt(java.time.LocalDateTime.now());
                            sensor.setUpdatedAt(java.time.LocalDateTime.now());

                            // Create signal config
                            SignalConfig signalConfig = new SignalConfig();
                            signalConfig.setName(formatSignalName(signalId));
                            signalConfig.setUnit(inferSignalUnit(signalId));

                            sensor.setSignalConfig(signalConfig);
                            sensorRepository.save(sensor);
                        }
                    }
                }

                // Assign/unassign factory
                if (factoryId == null) {
                    // Unassign from factory
                    plc.setFactory(null);
                } else {
                    // Assign to factory
                    Optional<Factory> factoryOpt = factoryRepository.findById(Long.parseLong(factoryId));
                    if (factoryOpt.isPresent()) {
                        plc.setFactory(factoryOpt.get());
                    }
                }

                plcRepository.save(plc);
            }

            return ResponseEntity.ok(Map.of("message", "Device assignments saved successfully"));
        } catch (Exception e) {
            log.error("Error saving device assignments", e);
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", "Failed to save device assignments"));
        }
    }

    private Map<String, Object> convertPlcToDevice(PLC plc) {
        // Get sensors for this PLC
        List<Sensor> sensors = sensorRepository.findByPlcId(plc.getId());

        List<Map<String, Object>> signalData = sensors.stream()
                .map(sensor -> {
                    Map<String, Object> signal = new HashMap<>();
                    signal.put("id", sensor.getId().toString());
                    signal.put("name", sensor.getSignalConfig().getName());
                    signal.put("type", sensor.getSignalConfig().getGenerator());
                    signal.put("unit", sensor.getSignalConfig().getUnit());
                    signal.put("deviceId", plc.getId().toString());
                    return signal;
                })
                .collect(Collectors.toList());

        Map<String, Object> device = new HashMap<>();
        device.put("id", plc.getPlcId());
        device.put("name", plc.getName());
        device.put("type", "PLC");
        device.put("factoryId", plc.getFactory() != null ? plc.getFactory().getId().toString() : null);
        device.put("signals", signalData);

        return device;
    }

    /**
     * Discover devices from plc_data table that are not already represented as PLC entities.
     * Groups device_ids by logical device names (e.g., Conveyor1_rpm and Conveyor1_status -> Conveyor1).
     */
    private List<Map<String, Object>> discoverDevicesFromPlcData(Set<String> existingPlcIds) {
        try {
            // Query distinct device_ids from plc_data
            List<String> allDeviceIds = plcDataRepository.findAllDistinctDeviceIds();
            log.debug("Found {} distinct device IDs in plc_data: {}", allDeviceIds.size(), allDeviceIds);

            // Group device_ids by logical device names
            Map<String, List<String>> deviceGroups = new HashMap<>();

            for (String deviceId : allDeviceIds) {
                // Skip if already exists as PLC entity
                if (existingPlcIds.contains(deviceId)) {
                    log.debug("Skipping device ID {} - already exists as PLC entity", deviceId);
                    continue;
                }

                // Extract logical device name (remove suffixes like _rpm, _status, _position)
                String logicalName = extractLogicalDeviceName(deviceId).toLowerCase();
                deviceGroups.computeIfAbsent(logicalName, k -> new ArrayList<>()).add(deviceId);
            }

            log.debug("Grouped into {} logical devices: {}", deviceGroups.size(), deviceGroups.keySet());

            // Convert grouped devices to device objects
            List<Map<String, Object>> devices = new ArrayList<>();
            for (Map.Entry<String, List<String>> entry : deviceGroups.entrySet()) {
                String logicalNameLower = entry.getKey();
                List<String> signalIds = entry.getValue();

                // Use the first signal ID to determine the proper case for the device ID
                final String deviceId;
                if (!signalIds.isEmpty()) {
                    // Extract the base name from the first signal (without suffix)
                    String firstSignal = signalIds.get(0);
                    deviceId = extractLogicalDeviceName(firstSignal);
                } else {
                    deviceId = logicalNameLower;
                }

                // Skip if this device ID already exists as a PLC entity
                if (existingPlcIds.contains(deviceId)) {
                    log.debug("Skipping discovered device ID {} - already exists as PLC entity", deviceId);
                    continue;
                }

                // Create signals for this device
                List<Map<String, Object>> signals = signalIds.stream()
                        .map(signalId -> {
                            Map<String, Object> signal = new HashMap<>();
                            signal.put("id", signalId);
                            signal.put("name", formatSignalName(signalId));
                            signal.put("type", inferSignalType(signalId));
                            signal.put("unit", inferSignalUnit(signalId));
                            signal.put("deviceId", deviceId);
                            return signal;
                        })
                        .collect(Collectors.toList());

                Map<String, Object> device = new HashMap<>();
                device.put("id", deviceId);
                device.put("name", formatDeviceName(deviceId));
                device.put("type", inferDeviceType(deviceId));
                device.put("factoryId", null); // Unassigned
                device.put("signals", signals);

                devices.add(device);
                log.debug("Created device: {} with {} signals", deviceId, signals.size());
            }

            log.debug("Returning {} discovered devices", devices.size());
            return devices;
        } catch (Exception e) {
            log.error("Error discovering devices from plc_data", e);
            return new ArrayList<>();
        }
    }

    private String extractLogicalDeviceName(String deviceId) {
        // Remove common suffixes to group related signals
        if (deviceId.endsWith("_rpm") || deviceId.endsWith("_status") ||
            deviceId.endsWith("_position") || deviceId.endsWith("_temp") ||
            deviceId.endsWith("_speed")) {
            return deviceId.substring(0, deviceId.lastIndexOf("_"));
        }
        return deviceId;
    }

    private String formatDeviceName(String logicalName) {
        if (logicalName == null || logicalName.trim().isEmpty()) {
            return "Unknown Device";
        }

        // Replace underscores with dashes for better readability
        String formatted = logicalName.replace("_", "-");

        // Capitalize first letter
        if (formatted.length() > 0) {
            formatted = formatted.substring(0, 1).toUpperCase() +
                       (formatted.length() > 1 ? formatted.substring(1) : "");
        }

        // Handle camelCase by inserting spaces before uppercase letters (but not for abbreviations)
        // This is a simple approach - just insert space before capital letters that follow lowercase
        formatted = formatted.replaceAll("([a-z])([A-Z])", "$1 $2");

        return formatted;
    }

    private String formatSignalName(String signalId) {
        // Extract the signal type from the suffix
        if (signalId.endsWith("_rpm")) return "RPM";
        if (signalId.endsWith("_status")) return "Status";
        if (signalId.endsWith("_position")) return "Position";
        if (signalId.endsWith("_temp")) return "Temperature";
        if (signalId.endsWith("_speed")) return "Speed";
        return signalId;
    }

    private String inferSignalType(String signalId) {
        if (signalId.endsWith("_rpm") || signalId.endsWith("_speed")) return "speed";
        if (signalId.endsWith("_status")) return "boolean";
        if (signalId.endsWith("_position")) return "position";
        if (signalId.endsWith("_temp")) return "temperature";
        return "numeric";
    }

    private String inferSignalUnit(String signalId) {
        if (signalId.endsWith("_rpm")) return "RPM";
        if (signalId.endsWith("_temp")) return "°C";
        if (signalId.endsWith("_position")) return "mm";
        if (signalId.endsWith("_speed")) return "m/s";
        return "";
    }

    private String inferDeviceType(String logicalName) {
        String lowerName = logicalName.toLowerCase();
        if (lowerName.contains("conveyor")) return "Conveyor";
        if (lowerName.contains("placer")) return "Component Placer";
        if (lowerName.contains("motor")) return "Motor";
        if (lowerName.contains("sensor")) return "Sensor";
        return "Device";
    }

    @PostMapping("/factories")
    public ResponseEntity<Map<String, Object>> createFactory(@RequestBody Map<String, Object> request) {
        try {
            String name = (String) request.get("name");
            String description = (String) request.get("description");
            String factoryId = (String) request.get("factoryId");

            if (name == null || name.trim().isEmpty()) {
                return ResponseEntity.badRequest()
                    .body(Map.of("error", "Factory name is required"));
            }

            // Generate factoryId if not provided
            if (factoryId == null || factoryId.trim().isEmpty()) {
                factoryId = name.toLowerCase().replaceAll("[^a-z0-9]", "-") + "-" + System.currentTimeMillis();
            }

            // Get the first manufacturer (for now, we can make this configurable later)
            Manufacturer manufacturer = manufacturerRepository.findAll().stream().findFirst()
                .orElseThrow(() -> new RuntimeException("No manufacturer found"));

            Factory factory = new Factory();
            factory.setFactoryId(factoryId);
            factory.setName(name);
            factory.setDescription(description);
            factory.setManufacturer(manufacturer);
            factory.setIsActive(true);
            factory.setCreatedAt(java.time.LocalDateTime.now());
            factory.setUpdatedAt(java.time.LocalDateTime.now());

            Factory savedFactory = factoryRepository.save(factory);

            Map<String, Object> response = new HashMap<>();
            response.put("id", savedFactory.getId().toString());
            response.put("factoryId", savedFactory.getFactoryId());
            response.put("name", savedFactory.getName());
            response.put("description", savedFactory.getDescription());
            response.put("devices", new ArrayList<>());

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Error creating factory", e);
            return ResponseEntity.internalServerError()
                .body(Map.of("error", "Failed to create factory"));
        }
    }

    @PutMapping("/factories/{id}")
    public ResponseEntity<Map<String, Object>> updateFactory(@PathVariable Long id, @RequestBody Map<String, Object> request) {
        try {
            Factory factory = factoryRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Factory not found"));

            String name = (String) request.get("name");
            String description = (String) request.get("description");

            if (name != null && !name.trim().isEmpty()) {
                factory.setName(name.trim());
            }
            if (description != null) {
                factory.setDescription(description.trim());
            }

            factory.setUpdatedAt(java.time.LocalDateTime.now());
            Factory savedFactory = factoryRepository.save(factory);

            Map<String, Object> response = new HashMap<>();
            response.put("id", savedFactory.getId().toString());
            response.put("factoryId", savedFactory.getFactoryId());
            response.put("name", savedFactory.getName());
            response.put("description", savedFactory.getDescription());

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Error updating factory", e);
            return ResponseEntity.internalServerError()
                .body(Map.of("error", "Failed to update factory"));
        }
    }

    @DeleteMapping("/factories/{id}")
    public ResponseEntity<Map<String, Object>> deleteFactory(@PathVariable Long id) {
        try {
            Factory factory = factoryRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Factory not found"));

            // Check if factory has devices assigned
            if (factory.getPlcs() != null && !factory.getPlcs().isEmpty()) {
                return ResponseEntity.badRequest()
                    .body(Map.of("error", "Cannot delete factory with assigned devices. Please unassign all devices first."));
            }

            factoryRepository.delete(factory);

            return ResponseEntity.ok(Map.of("message", "Factory deleted successfully"));
        } catch (Exception e) {
            log.error("Error deleting factory", e);
            return ResponseEntity.internalServerError()
                .body(Map.of("error", "Failed to delete factory"));
        }
    }
}