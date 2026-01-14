package com.virtplc.api;

import com.virtplc.model.Company;
import com.virtplc.model.Factory;
import com.virtplc.model.Manufacturer;
import com.virtplc.model.PLC;
import com.virtplc.model.PlcData;
import com.virtplc.model.Sensor;
import com.virtplc.model.SensorData;
import com.virtplc.model.Tenant;
import com.virtplc.repository.CompanyRepository;
import com.virtplc.repository.FactoryRepository;
import com.virtplc.repository.PLCRepository;
import com.virtplc.repository.PlcDataRepository;
import com.virtplc.repository.SensorRepository;
import com.virtplc.repository.ManufacturerRepository;
import com.virtplc.repository.TenantRepository;
import com.virtplc.service.DataService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.HttpMethod;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.annotation.Propagation;

/**
 * REST controller for sensor data and time-series queries.
 */
@Slf4j
@RestController
@RequestMapping("/api/data")
@RequiredArgsConstructor
public class DataController {

    private final DataService dataService;
    private final CompanyRepository companyRepository;
    private final TenantRepository tenantRepository;
    private final FactoryRepository factoryRepository;
    private final PLCRepository plcRepository;
    private final SensorRepository sensorRepository;
    private final PlcDataRepository plcDataRepository;
    private final ManufacturerRepository manufacturerRepository;
    private final RestTemplate restTemplate = new RestTemplate();

    /**
     * Get latest sensor readings from all devices.
     */
    @GetMapping("/latest")
    public ResponseEntity<SensorData> getLatestData(HttpServletRequest request) {
        log.debug("GET /api/data/latest");

        // Latest data is real-time and not filtered by user permissions
        SensorData sensorData = dataService.getLatestData(null);
        return ResponseEntity.ok(sensorData);
    }

    /**
     * Get historical data for a specific device
     */
    @GetMapping("/device/{deviceId}/history")
    public ResponseEntity<List<Map<String, Object>>> getDeviceHistory(
            @PathVariable String deviceId,
            @RequestParam Long startTime,
            @RequestParam Long endTime) {
        log.info("GET /api/data/device/{}/history?startTime={}&endTime={}", deviceId, startTime, endTime);

        // Input validation to prevent injection attacks
        if (deviceId == null || deviceId.trim().isEmpty() || deviceId.length() > 100) {
            log.warn("Invalid deviceId: {}", deviceId);
            return ResponseEntity.badRequest().body(List.of());
        }
        // Validate deviceId contains only safe characters
        if (!deviceId.matches("^[a-zA-Z0-9_-]+$")) {
            log.warn("DeviceId contains invalid characters: {}", deviceId);
            return ResponseEntity.badRequest().body(List.of());
        }
        // Validate time range
        if (startTime == null || endTime == null || startTime < 0 || endTime < 0 || endTime < startTime) {
            log.warn("Invalid time range: start={}, end={}", startTime, endTime);
            return ResponseEntity.badRequest().body(List.of());
        }
        // Prevent excessively large time ranges (max 30 days)
        long maxRange = 30L * 24L * 60L * 60L * 1000L; // 30 days in milliseconds
        if (endTime - startTime > maxRange) {
            log.warn("Time range too large: {} ms", endTime - startTime);
            return ResponseEntity.badRequest().body(List.of());
        }

        try {
            List<Map<String, Object>> history = plcDataRepository.findDeviceHistory(deviceId, startTime, endTime);
            log.info("Found {} historical data points for device {}", history.size(), deviceId);
            return ResponseEntity.ok(history);
        } catch (Exception e) {
            log.error("Error fetching device history for {}: {}", deviceId, e.getMessage());
            return ResponseEntity.status(500).body(List.of());
        }
    }

    /**
     * Extract manufacturers from authenticated user request attributes.
     * Admin users get all manufacturers, non-admin users get manufacturers from
     * their company.
     */
    private List<Manufacturer> getManufacturersFromRequest(HttpServletRequest request) {
        String userRole = (String) request.getAttribute("userRole");

        // Admin users can access all manufacturers
        if ("ADMIN".equals(userRole) || userRole == null) {
            // For admin or unauthenticated, return all manufacturers (we'll need to update
            // DataService to
            // handle this)
            return null; // Special case for admin
        }

        Long companyId = (Long) request.getAttribute("companyId");
        if (companyId == null) {
            log.error("No company ID found in request attributes for non-admin user");
            return List.of();
        }

        Company company = companyRepository.findById(companyId).orElse(null);
        if (company == null) {
            log.error("Company not found for ID: {}", companyId);
            return List.of();
        }

        return company.getManufacturers();
    }

    /**
     * NEW SIMPLIFIED ENDPOINT: Get hierarchical data ONLY from TimescaleDB.
     * Returns only devices with actual data (no empty PostgreSQL entities).
     */
    @GetMapping("/hierarchical-live")
    public ResponseEntity<Map<String, Object>> getHierarchicalLiveData() {
        log.info("GET /api/data/hierarchical-live - Getting live data from TimescaleDB");
        try {
            Map<String, Object> response = new HashMap<>();
            response.put("timestamp", System.currentTimeMillis());

            // Query TimescaleDB for all sensors (simulator data)
            List<PlcData> simulatorSensors = plcDataRepository.findLatestSensors();

            // Query TimescaleDB for Unreal devices
            List<PlcData> unrealDevices = plcDataRepository.findLatestUnrealDevices();

            log.info("Found {} simulator sensors and {} Unreal devices", simulatorSensors.size(), unrealDevices.size());

            // Group simulator sensors by PLC (extract from device_id like
            // "motor_speed_PLC-NY-001")
            Map<String, List<PlcData>> sensorsByPlc = simulatorSensors.stream()
                    .collect(Collectors.groupingBy(sensor -> extractPlcId(sensor.getDeviceId())));

            // Build tenant hierarchy from sensor metadata
            Map<String, Map<String, Map<String, List<String>>>> hierarchy = new HashMap<>();
            // hierarchy: tenant -> manufacturer -> factory -> list of PLC IDs

            // Process sensors to build hierarchy
            for (PlcData sensor : simulatorSensors) {
                if (sensor.getMetadata() == null)
                    continue;

                String tenant = sensor.getMetadata().path("tenant").asText("unknown");
                String factory = sensor.getMetadata().path("factory").asText("unknown");
                String plcId = extractPlcId(sensor.getDeviceId());

                // Determine manufacturer from factory name or use tenant
                String manufacturer = tenant + "-motors";

                hierarchy.putIfAbsent(tenant, new HashMap<>());
                hierarchy.get(tenant).putIfAbsent(manufacturer, new HashMap<>());
                hierarchy.get(tenant).get(manufacturer).putIfAbsent(factory, new ArrayList<>());

                if (!hierarchy.get(tenant).get(manufacturer).get(factory).contains(plcId)) {
                    hierarchy.get(tenant).get(manufacturer).get(factory).add(plcId);
                }
            }

            // Add Unreal devices to hierarchy if they exist
            if (!unrealDevices.isEmpty()) {
                hierarchy.putIfAbsent("accenture", new HashMap<>());
                hierarchy.get("accenture").putIfAbsent("accenture-manufacturing", new HashMap<>());
                hierarchy.get("accenture").get("accenture-manufacturing").putIfAbsent("test-factory",
                        new ArrayList<>());
            }

            // Build response structure
            List<Map<String, Object>> tenants = new ArrayList<>();

            for (Map.Entry<String, Map<String, Map<String, List<String>>>> tenantEntry : hierarchy.entrySet()) {
                String tenantId = tenantEntry.getKey();
                Map<String, Object> tenantMap = new HashMap<>();
                tenantMap.put("id", tenantId);
                tenantMap.put("name", capitalize(tenantId));

                List<Map<String, Object>> manufacturers = new ArrayList<>();

                for (Map.Entry<String, Map<String, List<String>>> mfgEntry : tenantEntry.getValue().entrySet()) {
                    String mfgId = mfgEntry.getKey();
                    Map<String, Object> mfgMap = new HashMap<>();
                    mfgMap.put("id", mfgId);
                    mfgMap.put("name", capitalize(mfgId));

                    List<Map<String, Object>> factories = new ArrayList<>();

                    for (Map.Entry<String, List<String>> factoryEntry : mfgEntry.getValue().entrySet()) {
                        String factoryId = factoryEntry.getKey();
                        Map<String, Object> factoryMap = new HashMap<>();
                        factoryMap.put("id", factoryId);
                        factoryMap.put("name", capitalize(factoryId));

                        List<Map<String, Object>> plcs = new ArrayList<>();

                        // Add each PLC with its sensors
                        for (String plcId : factoryEntry.getValue()) {
                            Map<String, Object> plcMap = new HashMap<>();
                            plcMap.put("id", plcId);
                            plcMap.put("name", plcId);

                            List<Map<String, Object>> sensors = new ArrayList<>();
                            List<PlcData> plcSensors = sensorsByPlc.get(plcId);

                            if (plcSensors != null) {
                                for (PlcData sensorData : plcSensors) {
                                    Map<String, Object> sensor = new HashMap<>();
                                    sensor.put("id", sensorData.getDeviceId());
                                    sensor.put("deviceId", sensorData.getDeviceId());

                                    // Extract sensor name from data.name
                                    String sensorName = sensorData.getData() != null
                                            ? sensorData.getData().path("name").asText(sensorData.getDeviceId())
                                            : sensorData.getDeviceId();
                                    sensor.put("name", sensorName);

                                    // Extract unit from data.signal_config.unit
                                    String unit = "";
                                    if (sensorData.getData() != null && sensorData.getData().has("signal_config")) {
                                        unit = sensorData.getData().path("signal_config").path("unit").asText("");
                                    }
                                    sensor.put("unit", unit);

                                    // Value is stored in rpm column for sensors
                                    sensor.put("value", sensorData.getRpm() != null ? sensorData.getRpm() : 0.0);
                                    sensor.put("timestamp",
                                            sensorData.getTimestamp().toInstant(ZoneOffset.UTC).toEpochMilli());

                                    sensors.add(sensor);
                                }
                            }

                            plcMap.put("sensors", sensors);
                            plcs.add(plcMap);
                        }

                        // Add Unreal devices to "accenture" tenant's "test-factory"
                        if ("test-factory".equalsIgnoreCase(factoryId)) {
                            for (PlcData unrealDevice : unrealDevices) {
                                Map<String, Object> plcMap = new HashMap<>();
                                plcMap.put("id", unrealDevice.getDeviceId());
                                plcMap.put("name", capitalize(unrealDevice.getDeviceId()));

                                List<Map<String, Object>> sensors = new ArrayList<>();
                                long timestamp = unrealDevice.getTimestamp().toInstant(ZoneOffset.UTC).toEpochMilli();

                                // Add RPM if present
                                if (unrealDevice.getRpm() != null && unrealDevice.getRpm() != 0.0) {
                                    Map<String, Object> sensor = new HashMap<>();
                                    String sensorId = unrealDevice.getDeviceId() + "_rpm";
                                    sensor.put("id", sensorId);
                                    sensor.put("deviceId", unrealDevice.getDeviceId()); // Use base device_id for
                                                                                        // history queries
                                    sensor.put("name", "RPM");
                                    sensor.put("unit", "rpm");
                                    sensor.put("value", unrealDevice.getRpm());
                                    sensor.put("timestamp", timestamp);
                                    sensors.add(sensor);
                                }

                                // Add position_x if present
                                if (unrealDevice.getPositionX() != null && unrealDevice.getPositionX() != 0.0) {
                                    Map<String, Object> sensor = new HashMap<>();
                                    String sensorId = unrealDevice.getDeviceId() + "_position_x";
                                    sensor.put("id", sensorId);
                                    sensor.put("deviceId", unrealDevice.getDeviceId()); // Use base device_id for
                                                                                        // history queries
                                    sensor.put("name", "Position_X");
                                    sensor.put("unit", "");
                                    sensor.put("value", unrealDevice.getPositionX());
                                    sensor.put("timestamp", timestamp);
                                    sensors.add(sensor);
                                }

                                // Add position_y if present
                                if (unrealDevice.getPositionY() != null && unrealDevice.getPositionY() != 0.0) {
                                    Map<String, Object> sensor = new HashMap<>();
                                    String sensorId = unrealDevice.getDeviceId() + "_position_y";
                                    sensor.put("id", sensorId);
                                    sensor.put("deviceId", unrealDevice.getDeviceId()); // Use base device_id for
                                                                                        // history queries
                                    sensor.put("name", "Position_Y");
                                    sensor.put("unit", "");
                                    sensor.put("value", unrealDevice.getPositionY());
                                    sensor.put("timestamp", timestamp);
                                    sensors.add(sensor);
                                }

                                if (!sensors.isEmpty()) {
                                    plcMap.put("sensors", sensors);
                                    plcs.add(plcMap);
                                }
                            }
                        }

                        factoryMap.put("plcs", plcs);
                        factories.add(factoryMap);
                    }

                    mfgMap.put("factories", factories);
                    manufacturers.add(mfgMap);
                }

                tenantMap.put("manufacturers", manufacturers);
                tenants.add(tenantMap);
            }

            response.put("tenants", tenants);
            log.info("Returning {} tenants with live data", tenants.size());

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Error fetching live hierarchical data", e);
            return ResponseEntity.internalServerError().build();
        }
    }

    /**
     * Helper method to extract PLC ID from sensor device_id.
     * Example: "motor_speed_PLC-NY-001" -> "PLC-NY-001"
     */
    private String extractPlcId(String deviceId) {
        if (deviceId == null)
            return "UNKNOWN";

        // Find "PLC-" in the string
        int plcIndex = deviceId.indexOf("PLC-");
        if (plcIndex >= 0) {
            return deviceId.substring(plcIndex);
        }

        return deviceId;
    }

    /**
     * Get hierarchical data from database (TimescaleDB) instead of simulator.
     */
    @GetMapping("/hierarchical")
    @Transactional
    public ResponseEntity<String> getHierarchicalData(HttpServletRequest request) {
        log.info("GET /api/data/hierarchical - Starting hierarchical data retrieval");
        try {
            // Ensure manufacturers and factories exist based on plc_data metadata
            ensureHierarchy();

            // Query Unreal Engine devices ONCE before the loop
            List<PlcData> unrealDevices = plcDataRepository.findLatestForAllDevices();
            log.info("Found {} Unreal Engine devices", unrealDevices.size());

            // Get manufacturers based on user permissions
            List<Manufacturer> manufacturers = getManufacturersFromRequest(request);
            log.info("Found {} manufacturers", manufacturers != null ? manufacturers.size() : "all");

            // Get all factories for the user's manufacturers
            // Be defensive: filter out any factories with null manufacturer to avoid NPEs
            List<Factory> factories = factoryRepository.findAll().stream()
                    .filter(factory -> factory.getManufacturer() != null)
                    .filter(factory -> manufacturers == null ||
                            manufacturers.stream().anyMatch(m -> m.getId().equals(factory.getManufacturer().getId())))
                    .collect(Collectors.toList());
            log.info("Found {} factories", factories.size());

            // Get ALL distinct manufacturers from factories (for building hierarchy)
            List<Manufacturer> allManufacturers = factories.stream()
                    .map(Factory::getManufacturer)
                    .filter(m -> m != null)
                    .distinct()
                    .collect(Collectors.toList());
            log.info("Found {} distinct manufacturers from factories", allManufacturers.size());

            // Build hierarchical structure
            Map<String, Object> response = new HashMap<>();
            response.put("timestamp", System.currentTimeMillis());

            List<Map<String, Object>> tenantData = new ArrayList<>();

            // Group factories by manufacturer and then by tenant
            Map<Long, List<Factory>> factoriesByManufacturer = factories.stream()
                    .filter(f -> f.getManufacturer() != null && f.getManufacturer().getId() != null)
                    .collect(Collectors.groupingBy(f -> f.getManufacturer().getId()));
            log.info("Grouped factories into {} manufacturer groups", factoriesByManufacturer.size());

            // Group manufacturers by tenant
            Map<String, List<Manufacturer>> manufacturersByTenant = allManufacturers.stream()
                    .filter(m -> m.getTenant() != null)
                    .collect(Collectors.groupingBy(m -> m.getTenant().getTenantId()));
            log.info("Grouped manufacturers into {} tenant groups", manufacturersByTenant.size());
            log.info("Tenant IDs: {}", manufacturersByTenant.keySet());

            // Build tenant hierarchy
            for (Map.Entry<String, List<Manufacturer>> tenantEntry : manufacturersByTenant.entrySet()) {
                String tenantId = tenantEntry.getKey();
                List<Manufacturer> tenantManufacturers = tenantEntry.getValue();

                Map<String, Object> tenant = new HashMap<>();
                tenant.put("id", tenantId);
                // Get tenant name from first manufacturer's tenant
                tenant.put("name", tenantManufacturers.get(0).getTenant().getName());

                List<Map<String, Object>> manufacturerData = new ArrayList<>();

                // Process only manufacturers that belong to this tenant
                for (Manufacturer manufacturer : tenantManufacturers) {
                    // Find factories for this manufacturer
                    List<Factory> manufacturerFactories = factoriesByManufacturer.get(manufacturer.getId());
                    if (manufacturerFactories == null || manufacturerFactories.isEmpty()) {
                        continue;
                    }

                    Map<String, Object> manufacturerMap = new HashMap<>();
                    manufacturerMap.put("id", manufacturer.getManufacturerId());
                    manufacturerMap.put("name", manufacturer.getName());

                    List<Map<String, Object>> factoryData = new ArrayList<>();

                    for (Factory factory : manufacturerFactories) {
                        Map<String, Object> factoryMap = new HashMap<>();
                        factoryMap.put("id", factory.getFactoryId());
                        factoryMap.put("name", factory.getName());

                        // Get PLCs for this factory
                        List<PLC> plcs = plcRepository.findByFactoryId(factory.getId());
                        List<Map<String, Object>> plcData = new ArrayList<>();

                        for (PLC plc : plcs) {
                            Map<String, Object> plcMap = new HashMap<>();
                            plcMap.put("id", plc.getPlcId());
                            plcMap.put("name", plc.getName());

                            // Get sensors for this PLC
                            List<Sensor> sensors = sensorRepository.findByPlcId(plc.getId());
                            List<Map<String, Object>> sensorData = new ArrayList<>();

                            for (Sensor sensor : sensors) {
                                Map<String, Object> sensorMap = new HashMap<>();
                                String sensorId = sensor.getSensorId();
                                sensorMap.put("id", sensorId != null ? sensorId : "unknown");
                                sensorMap.put("name", sensor.getName());
                                sensorMap.put("unit",
                                        sensor.getSignalConfig() != null ? sensor.getSignalConfig().getUnit() : "");

                                try {
                                    // Get latest reading from TimescaleDB (defensive)
                                    PlcData latestData = null;

                                    // Try to query by sensor_id first (matches device_id in plc_data table)
                                    latestData = plcDataRepository.findLatestByDeviceId(sensorId);

                                    // If not found and we have a PLC, try PLC ID
                                    if (latestData == null) {
                                        PLC sensorPlc = sensor.getPlc();
                                        if (sensorPlc != null && sensorPlc.getPlcId() != null) {
                                            latestData = plcDataRepository.findLatestByDeviceId(sensorPlc.getPlcId());
                                        }
                                    }

                                    if (latestData != null) {
                                        // Extract value from PlcData based on sensor type
                                        Double value = extractValueFromPlcData(latestData, sensor);
                                        sensorMap.put("value", value != null ? value : 0.0);
                                        sensorMap.put("timestamp",
                                                latestData.getTimestamp().toInstant(ZoneOffset.UTC).toEpochMilli());

                                        // For placer sensor, also include position_x and position_y
                                        if (sensor.getName().equalsIgnoreCase("placer")) {
                                            sensorMap.put("position_x",
                                                    latestData.getPositionX() != null ? latestData.getPositionX()
                                                            : 0.0);
                                            sensorMap.put("position_y",
                                                    latestData.getPositionY() != null ? latestData.getPositionY()
                                                            : 0.0);
                                        }
                                    } else {
                                        sensorMap.put("value", 0.0);
                                        sensorMap.put("timestamp", System.currentTimeMillis());

                                        // For placer sensor, also include position_x and position_y
                                        if (sensor.getName().equalsIgnoreCase("placer")) {
                                            sensorMap.put("position_x", 0.0);
                                            sensorMap.put("position_y", 0.0);
                                        }
                                    }
                                } catch (Exception ex) {
                                    log.warn("Failed to fetch latest PlcData for sensor {}: {}", sensorId,
                                            ex.getMessage());
                                    sensorMap.put("value", 0.0);
                                    sensorMap.put("timestamp", System.currentTimeMillis());
                                }

                                sensorData.add(sensorMap);
                            }

                            plcMap.put("sensors", sensorData);
                            plcData.add(plcMap);
                        }

                        // Add Unreal Engine devices as additional PLCs (use pre-fetched data)
                        for (PlcData unrealDevice : unrealDevices) {
                            // Only add UNREAL type devices
                            if ("UNREAL".equals(unrealDevice.getType())) {
                                Map<String, Object> unrealPlcMap = new HashMap<>();
                                unrealPlcMap.put("id", unrealDevice.getDeviceId());
                                unrealPlcMap.put("name", capitalize(unrealDevice.getDeviceId()));
                                unrealPlcMap.put("description", "Unreal Engine Device");

                                List<Map<String, Object>> unrealSensorData = new ArrayList<>();

                                // Dynamically extract all non-null numeric fields from the device
                                long timestamp = unrealDevice.getTimestamp().toInstant(ZoneOffset.UTC).toEpochMilli();

                                // Add RPM if present
                                if (unrealDevice.getRpm() != null && unrealDevice.getRpm() != 0.0) {
                                    Map<String, Object> sensor = new HashMap<>();
                                    sensor.put("id", unrealDevice.getDeviceId() + "_rpm");
                                    sensor.put("deviceId", unrealDevice.getDeviceId()); // Use base device_id for
                                                                                        // history queries
                                    sensor.put("name", "RPM");
                                    sensor.put("unit", "rpm");
                                    sensor.put("value", unrealDevice.getRpm());
                                    sensor.put("timestamp", timestamp);
                                    unrealSensorData.add(sensor);
                                }

                                // Add position_x if present and non-zero
                                if (unrealDevice.getPositionX() != null && unrealDevice.getPositionX() != 0.0) {
                                    Map<String, Object> sensor = new HashMap<>();
                                    sensor.put("id", unrealDevice.getDeviceId() + "_position_x");
                                    sensor.put("deviceId", unrealDevice.getDeviceId()); // Use base device_id for
                                                                                        // history queries
                                    sensor.put("name", "Position_X");
                                    sensor.put("unit", "");
                                    sensor.put("value", unrealDevice.getPositionX());
                                    sensor.put("timestamp", timestamp);
                                    unrealSensorData.add(sensor);
                                }

                                // Add position_y if present and non-zero
                                if (unrealDevice.getPositionY() != null && unrealDevice.getPositionY() != 0.0) {
                                    Map<String, Object> sensor = new HashMap<>();
                                    sensor.put("id", unrealDevice.getDeviceId() + "_position_y");
                                    sensor.put("deviceId", unrealDevice.getDeviceId()); // Use base device_id for
                                                                                        // history queries
                                    sensor.put("name", "Position_Y");
                                    sensor.put("unit", "");
                                    sensor.put("value", unrealDevice.getPositionY());
                                    sensor.put("timestamp", timestamp);
                                    unrealSensorData.add(sensor);
                                }

                                // Add is_on if present
                                if (unrealDevice.getIsOn() != null) {
                                    Map<String, Object> sensor = new HashMap<>();
                                    sensor.put("id", unrealDevice.getDeviceId() + "_is_on");
                                    sensor.put("name", "Is_On");
                                    sensor.put("unit", "");
                                    sensor.put("value", unrealDevice.getIsOn() ? 1.0 : 0.0);
                                    sensor.put("timestamp", timestamp);
                                    unrealSensorData.add(sensor);
                                }

                                // Add in_operation if present
                                if (unrealDevice.getInOperation() != null) {
                                    Map<String, Object> sensor = new HashMap<>();
                                    sensor.put("id", unrealDevice.getDeviceId() + "_in_operation");
                                    sensor.put("name", "In_Operation");
                                    sensor.put("unit", "");
                                    sensor.put("value", unrealDevice.getInOperation() ? 1.0 : 0.0);
                                    sensor.put("timestamp", timestamp);
                                    unrealSensorData.add(sensor);
                                }

                                // Add the PLC only if it has at least one sensor
                                if (!unrealSensorData.isEmpty()) {
                                    unrealPlcMap.put("sensors", unrealSensorData);
                                    plcData.add(unrealPlcMap);
                                }
                            }
                        }

                        factoryMap.put("plcs", plcData);
                        factoryData.add(factoryMap);
                    }

                    manufacturerMap.put("factories", factoryData);
                    manufacturerData.add(manufacturerMap);
                } // End manufacturer loop

                tenant.put("manufacturers", manufacturerData);
                log.info("Adding tenant '{}' with {} manufacturers", tenantId, manufacturerData.size());
                tenantData.add(tenant);
            } // End tenant loop

            response.put("tenants", tenantData);
            log.info("Returning {} tenants in response", tenantData.size());

            ObjectMapper objectMapper = new ObjectMapper();
            String jsonResponse = objectMapper.writeValueAsString(response);

            return ResponseEntity.ok(jsonResponse);
        } catch (Exception e) {
            log.error("Error fetching hierarchical data from database", e);
            return ResponseEntity.internalServerError().body("Failed to fetch data from database");
        }
    }

    /**
     * Get latest Unreal Engine PLC data (conveyor1, conveyor2, placer1).
     * This endpoint serves data from the plc_data table that comes through:
     * Unreal Engine → MQTT → Node-RED → Collector → TimescaleDB
     */
    @GetMapping("/plc-data/latest")
    public ResponseEntity<List<Map<String, Object>>> getLatestPlcData() {
        log.info("GET /api/data/plc-data/latest - Fetching latest Unreal PLC data");

        try {
            List<PlcData> latestData = plcDataRepository.findLatestForAllDevices();

            List<Map<String, Object>> response = latestData.stream()
                    .map(plcData -> {
                        Map<String, Object> deviceMap = new HashMap<>();
                        deviceMap.put("device_id", plcData.getDeviceId());
                        deviceMap.put("timestamp", plcData.getTimestamp().toEpochSecond(ZoneOffset.UTC) * 1000);
                        deviceMap.put("type", plcData.getType());

                        // Add numeric fields if present
                        if (plcData.getRpm() != null) {
                            deviceMap.put("rpm", plcData.getRpm());
                        }
                        if (plcData.getPositionX() != null) {
                            deviceMap.put("position_x", plcData.getPositionX());
                        }
                        if (plcData.getPositionY() != null) {
                            deviceMap.put("position_y", plcData.getPositionY());
                        }
                        if (plcData.getIsOn() != null) {
                            deviceMap.put("is_on", plcData.getIsOn());
                        }
                        if (plcData.getInOperation() != null) {
                            deviceMap.put("in_operation", plcData.getInOperation());
                        }

                        // Add JSONB fields if present
                        if (plcData.getData() != null) {
                            deviceMap.put("data", plcData.getData());
                        }
                        if (plcData.getMetadata() != null) {
                            deviceMap.put("metadata", plcData.getMetadata());
                        }

                        return deviceMap;
                    })
                    .collect(Collectors.toList());

            log.info("Found {} Unreal PLC devices with latest data", response.size());
            return ResponseEntity.ok(response);

        } catch (Exception e) {
            log.error("Error fetching latest PLC data", e);
            return ResponseEntity.internalServerError().build();
        }
    }

    /**
     * Ensure manufacturers and factories exist based on plc_data metadata.
     */
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    private void ensureHierarchy() {
        try {
            // Get all latest plc_data to extract tenant/factory from metadata
            List<PlcData> allData = plcDataRepository.findLatestForAllDevices();

            Set<String> tenants = new HashSet<>();
            Map<String, Set<String>> tenantFactories = new HashMap<>();

            for (PlcData data : allData) {
                if (data.getMetadata() != null) {
                    JsonNode tenantNode = data.getMetadata().get("tenant");
                    JsonNode factoryNode = data.getMetadata().get("factory");
                    String tenant = tenantNode != null ? tenantNode.asText() : null;
                    String factory = factoryNode != null ? factoryNode.asText() : null;
                    if (tenant != null && factory != null) {
                        tenants.add(tenant);
                        tenantFactories.computeIfAbsent(tenant, k -> new HashSet<>()).add(factory);
                    }
                }
            }

            // Create tenants
            for (String tenantId : tenants) {
                if (tenantRepository.findByTenantId(tenantId).isEmpty()) {
                    Tenant tenant = new Tenant();
                    tenant.setTenantId(tenantId);
                    tenant.setName(tenantId.toUpperCase().replace("-", " "));
                    tenant.setIsActive(true);
                    tenant.setCreatedAt(java.time.LocalDateTime.now());
                    tenant.setUpdatedAt(java.time.LocalDateTime.now());
                    tenantRepository.save(tenant);
                    log.info("Created tenant: {}", tenantId);
                }
            }

            // Create manufacturers
            for (String tenant : tenants) {
                Tenant tenantEntity = tenantRepository.findByTenantId(tenant).orElse(null);
                if (tenantEntity == null) {
                    // Should not happen, but skip
                    continue;
                }
                Optional<Manufacturer> existing = manufacturerRepository.findByManufacturerId(tenant);
                if (existing.isEmpty()) {
                    Manufacturer manufacturer = new Manufacturer();
                    manufacturer.setManufacturerId(tenant);
                    manufacturer.setName(tenant.toUpperCase().replace("-", " "));
                    manufacturer.setTenant(tenantEntity);
                    manufacturer.setCreatedAt(java.time.LocalDateTime.now());
                    manufacturer.setUpdatedAt(java.time.LocalDateTime.now());
                    manufacturerRepository.save(manufacturer);
                    log.info("Created manufacturer: {}", tenant);
                } else {
                    // Update existing to set tenant if not set
                    Manufacturer manufacturer = existing.get();
                    if (manufacturer.getTenant() == null) {
                        manufacturer.setTenant(tenantEntity);
                        manufacturer.setUpdatedAt(java.time.LocalDateTime.now());
                        manufacturerRepository.save(manufacturer);
                        log.info("Updated manufacturer: {} with tenant", tenant);
                    }
                }
            }

            // Create factories
            for (Map.Entry<String, Set<String>> entry : tenantFactories.entrySet()) {
                String tenant = entry.getKey();
                Manufacturer manufacturer = manufacturerRepository.findByManufacturerId(tenant).orElse(null);
                if (manufacturer != null) {
                    for (String factoryId : entry.getValue()) {
                        Optional<Factory> existingFactory = factoryRepository.findByFactoryId(factoryId);
                        if (existingFactory.isEmpty()) {
                            Factory factory = new Factory();
                            factory.setFactoryId(factoryId);
                            factory.setName(factoryId.replace("-", " ").toUpperCase());
                            factory.setManufacturer(manufacturer);
                            factory.setCreatedAt(java.time.LocalDateTime.now());
                            factory.setUpdatedAt(java.time.LocalDateTime.now());
                            factoryRepository.save(factory);
                            log.info("Created factory: {} under manufacturer: {}", factoryId, tenant);
                        } else {
                            // Update existing to set manufacturer if not set or different
                            Factory factory = existingFactory.get();
                            if (factory.getManufacturer() == null
                                    || !factory.getManufacturer().getId().equals(manufacturer.getId())) {
                                factory.setManufacturer(manufacturer);
                                factory.setUpdatedAt(java.time.LocalDateTime.now());
                                factoryRepository.save(factory);
                                log.info("Updated factory: {} with manufacturer: {}", factoryId, tenant);
                            }
                        }
                    }
                }
            }
        } catch (Exception e) {
            log.error("Error ensuring hierarchy", e);
        }
    }

    /**
     * Extract sensor value from PlcData based on sensor configuration.
     */
    private Double extractValueFromPlcData(PlcData plcData, Sensor sensor) {
        if (plcData == null)
            return null;

        // Try different fields based on sensor type or name
        String sensorName = sensor.getName().toLowerCase();

        // Check specific field matches first (more precise)
        if (sensorName.contains("rpm") && plcData.getRpm() != null) {
            return plcData.getRpm();
        }
        if (sensorName.contains("position") && sensorName.contains("x") && plcData.getPositionX() != null) {
            return plcData.getPositionX();
        }
        if (sensorName.contains("position") && sensorName.contains("y") && plcData.getPositionY() != null) {
            return plcData.getPositionY();
        }
        // Handle placer sensor - return position_x as primary value
        if (sensorName.equals("placer") && plcData.getPositionX() != null) {
            return plcData.getPositionX();
        }
        if ((sensorName.equals("status") || sensorName.equals("is_on") || sensorName.endsWith("_on"))
                && plcData.getIsOn() != null) {
            return plcData.getIsOn() ? 1.0 : 0.0;
        }
        if ((sensorName.equals("operation") || sensorName.equals("in_operation") || sensorName.endsWith("_operation"))
                && plcData.getInOperation() != null) {
            return plcData.getInOperation() ? 1.0 : 0.0;
        }

        // Try to extract from JSON data field
        if (plcData.getData() != null) {
            try {
                JsonNode dataNode = plcData.getData();
                if (dataNode.has(sensor.getSensorId())) {
                    return dataNode.get(sensor.getSensorId()).asDouble();
                }
                // Try with sensor name
                if (dataNode.has(sensor.getName())) {
                    return dataNode.get(sensor.getName()).asDouble();
                }
                // Try signal_config.value (Python simulator format)
                if (dataNode.has("signal_config")) {
                    JsonNode signalConfig = dataNode.get("signal_config");
                    if (signalConfig.has("value")) {
                        return signalConfig.get("value").asDouble();
                    }
                }
            } catch (Exception e) {
                log.debug("Could not extract value from JSON data for sensor {}", sensor.getSensorId());
            }
        }

        // As a fallback, if no specific match and RPM column has a value, use it
        if (plcData.getRpm() != null && plcData.getRpm() > 0) {
            return plcData.getRpm();
        }

        return null;
    }

    private String capitalize(String str) {
        if (str == null || str.isEmpty()) {
            return str;
        }
        return str.substring(0, 1).toUpperCase() + str.substring(1);
    }
}
