package com.virtplc.api;

import com.virtplc.model.SensorData;
import com.virtplc.service.DataService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

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

    /**
     * Get latest sensor readings from all devices.
     */
    @GetMapping("/latest")
    public ResponseEntity<SensorData> getLatestData() {
        log.debug("GET /api/data/latest");
        SensorData data = dataService.getLatestData();
        return ResponseEntity.ok(data);
    }

    /**
     * Get historical data for a time range.
     * @param startTime Start timestamp in milliseconds
     * @param endTime End timestamp in milliseconds
     */
    @GetMapping("/range")
    public ResponseEntity<List<SensorData>> getDataRange(
            @RequestParam Long startTime,
            @RequestParam Long endTime) {
        log.debug("GET /api/data/range?startTime={}&endTime={}", startTime, endTime);
        List<SensorData> data = dataService.getDataRange(startTime, endTime);
        return ResponseEntity.ok(data);
    }

    /**
     * Health check endpoint.
     */
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("DataController is running");
    }
}
