package com.virtplc.api;

import com.virtplc.model.Company;
import com.virtplc.model.Factory;
import com.virtplc.model.Manufacturer;
import com.virtplc.model.PLC;
import com.virtplc.model.PlcData;
import com.virtplc.model.Sensor;
import com.virtplc.model.SensorData;
import com.virtplc.repository.CompanyRepository;
import com.virtplc.repository.FactoryRepository;
import com.virtplc.repository.PLCRepository;
import com.virtplc.repository.PlcDataRepository;
import com.virtplc.repository.SensorRepository;
import com.virtplc.service.DataService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.HttpMethod;

/**
 * REST controller for sensor data and time-series queries.
 */
@Slf4j
@RestController
@RequestMapping("/api/data")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class DataController {

    private final DataService dataService;
    private final CompanyRepository companyRepository;
    private final FactoryRepository factoryRepository;
    private final PLCRepository plcRepository;
    private final SensorRepository sensorRepository;
    private final PlcDataRepository plcDataRepository;
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
     * Get historical data for a time range.
     * 
     * @param startTime Start timestamp in milliseconds
     * @param endTime   End timestamp in milliseconds
     */
    @GetMapping("/range")
    public ResponseEntity<List<SensorData>> getDataRange(
            @RequestParam Long startTime,
            @RequestParam Long endTime,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "1000") int size,
            HttpServletRequest request) {
        log.debug("GET /api/data/range?startTime={}&endTime={}&page={}&size={}", startTime, endTime, page, size);

        // For now, allow access to historical data without manufacturer filtering
        // TODO: Implement proper manufacturer-based filtering for production
        List<SensorData> data = dataService.getDataRange(null, startTime, endTime, page, size);
        return ResponseEntity.ok(data);
    }

    /**
     * Extract manufacturers from authenticated user request attributes.
     * Admin users get all manufacturers, non-admin users get manufacturers from
     * their company.
     */
    private List<Manufacturer> getManufacturersFromRequest(HttpServletRequest request) {
        String userRole = (String) request.getAttribute("userRole");

        // Admin users can access all manufacturers
        if ("ADMIN".equals(userRole)) {
            // For admin, return all manufacturers (we'll need to update DataService to
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
     * Get hierarchical data from database (TimescaleDB) instead of simulator.
     */
    @GetMapping("/hierarchical")
    public ResponseEntity<String> getHierarchicalData(HttpServletRequest request) {
        log.info("GET /api/data/hierarchical - Starting hierarchical data retrieval");
        try {
            // Get manufacturers based on user permissions
            List<Manufacturer> manufacturers = getManufacturersFromRequest(request);
            log.info("Found {} manufacturers", manufacturers != null ? manufacturers.size() : 0);

            // Get all factories for the user's manufacturers
            List<Factory> factories = factoryRepository.findAll().stream()
                    .filter(factory -> manufacturers == null ||
                            manufacturers.stream().anyMatch(m -> m.getId().equals(factory.getManufacturer().getId())))
                    .collect(Collectors.toList());
            log.info("Found {} factories", factories.size());

            // Build hierarchical structure
            Map<String, Object> response = new HashMap<>();
            response.put("timestamp", System.currentTimeMillis());

            List<Map<String, Object>> tenantData = new ArrayList<>();

            // Group factories by tenant (we'll use a single tenant for now)
            Map<String, Object> tenant = new HashMap<>();
            tenant.put("id", "accenture-tenant");
            tenant.put("name", "Accenture Manufacturing");

            List<Map<String, Object>> manufacturerData = new ArrayList<>();

            // Group factories by manufacturer
            Map<Long, List<Factory>> factoriesByManufacturer = factories.stream()
                    .collect(Collectors.groupingBy(f -> f.getManufacturer().getId()));
            log.info("Grouped factories into {} manufacturer groups", factoriesByManufacturer.size());

            for (Map.Entry<Long, List<Factory>> entry : factoriesByManufacturer.entrySet()) {
                Long manufacturerId = entry.getKey();
                List<Factory> manufacturerFactories = entry.getValue();
                Manufacturer manufacturer = manufacturerFactories.get(0).getManufacturer();

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
                            // Get latest reading from TimescaleDB
                            PlcData latestData = plcDataRepository.findLatestByDeviceId(sensor.getSensorId());

                            Map<String, Object> sensorMap = new HashMap<>();
                            sensorMap.put("id", sensor.getSensorId());
                            sensorMap.put("name", sensor.getName());
                            sensorMap.put("unit",
                                    sensor.getSignalConfig() != null ? sensor.getSignalConfig().getUnit() : "");

                            if (latestData != null) {
                                // Extract value from PlcData based on sensor type
                                Double value = extractValueFromPlcData(latestData, sensor);
                                sensorMap.put("value", value != null ? value : 0.0);
                                sensorMap.put("timestamp",
                                        latestData.getTimestamp().toInstant(ZoneOffset.UTC).toEpochMilli());
                            } else {
                                sensorMap.put("value", 0.0);
                                sensorMap.put("timestamp", System.currentTimeMillis());
                            }

                            sensorData.add(sensorMap);
                        }

                        plcMap.put("sensors", sensorData);
                        plcData.add(plcMap);
                    }

                    factoryMap.put("plcs", plcData);
                    factoryData.add(factoryMap);
                }

                manufacturerMap.put("factories", factoryData);
                manufacturerData.add(manufacturerMap);
            }

            tenant.put("manufacturers", manufacturerData);
            tenantData.add(tenant);
            response.put("tenants", tenantData);

            ObjectMapper objectMapper = new ObjectMapper();
            String jsonResponse = objectMapper.writeValueAsString(response);

            return ResponseEntity.ok(jsonResponse);
        } catch (Exception e) {
            log.error("Error fetching hierarchical data from database", e);
            return ResponseEntity.internalServerError().body("Failed to fetch data from database");
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

        if (sensorName.contains("rpm") && plcData.getRpm() != null) {
            return plcData.getRpm();
        }
        if (sensorName.contains("position") && sensorName.contains("x") && plcData.getPositionX() != null) {
            return plcData.getPositionX();
        }
        if (sensorName.contains("position") && sensorName.contains("y") && plcData.getPositionY() != null) {
            return plcData.getPositionY();
        }
        if (sensorName.contains("status") || sensorName.contains("on")) {
            return plcData.getIsOn() != null && plcData.getIsOn() ? 1.0 : 0.0;
        }
        if (sensorName.contains("operation")) {
            return plcData.getInOperation() != null && plcData.getInOperation() ? 1.0 : 0.0;
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
            } catch (Exception e) {
                log.debug("Could not extract value from JSON data for sensor {}", sensor.getSensorId());
            }
        }

        return null;
    }
}
