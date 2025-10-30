package com.virtplc.api;

import com.virtplc.model.Company;
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
            HttpServletRequest request) {
        log.debug("GET /api/data/range?startTime={}&endTime={}", startTime, endTime);

        Company company = getCompanyFromRequest(request);
        if (company == null) {
            return ResponseEntity.badRequest().build();
        }

        List<SensorData> data = dataService.getDataRange(company, startTime, endTime);
        return ResponseEntity.ok(data);
    }

    /**
     * Extract company from authenticated user request attributes.
     */
    private Company getCompanyFromRequest(HttpServletRequest request) {
        Long companyId = (Long) request.getAttribute("companyId");
        if (companyId == null) {
            log.error("No company ID found in request attributes");
            return null;
        }

        return companyRepository.findById(companyId).orElse(null);
    }

    /**
     * Health check endpoint.
     */
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("DataController is running");
    }
}
