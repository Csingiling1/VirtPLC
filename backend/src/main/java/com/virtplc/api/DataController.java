package com.virtplc.api;

import com.virtplc.model.Company;
import com.virtplc.model.Manufacturer;
import com.virtplc.model.SensorData;
import com.virtplc.repository.CompanyRepository;
import com.virtplc.service.DataService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.HttpServletRequest;
import java.util.List;

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

        List<Manufacturer> manufacturers = getManufacturersFromRequest(request);
        if (manufacturers != null && manufacturers.isEmpty()) {
            return ResponseEntity.badRequest().build();
        }

        List<SensorData> data = dataService.getDataRange(manufacturers, startTime, endTime, page, size);
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
     * Health check endpoint.
     */
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("DataController is running");
    }
}
