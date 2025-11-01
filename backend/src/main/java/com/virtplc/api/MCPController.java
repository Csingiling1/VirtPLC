package com.virtplc.api;

import com.virtplc.mcp.TimescaleMCPServer;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * MCP (Model Context Protocol) REST API Controller
 * Exposes TimescaleDB queries for AI services
 */
@RestController
@RequestMapping("/mcp")
@RequiredArgsConstructor
@Slf4j
@ConditionalOnProperty(name = "mcp.enabled", havingValue = "true")
@CrossOrigin(origins = "*")
public class MCPController {

    private final TimescaleMCPServer mcpServer;

    /**
     * Get sensor data by time range with optional filters
     */
    @GetMapping("/sensor-data")
    public ResponseEntity<Map<String, Object>> getSensorData(
            @RequestParam(required = false) String startTime,
            @RequestParam(required = false) String endTime,
            @RequestParam(required = false) String manufacturerId,
            @RequestParam(required = false) String factoryId,
            @RequestParam(required = false) String plcId,
            @RequestParam(required = false) String sensorId) {

        try {
            List<Map<String, Object>> data = mcpServer.querySensorDataByTimeRange(
                    startTime, endTime, manufacturerId, factoryId, plcId, sensorId);

            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "count", data.size(),
                    "data", data));
        } catch (Exception e) {
            log.error("Error querying sensor data", e);
            return ResponseEntity.badRequest().body(Map.of(
                    "success", false,
                    "error", e.getMessage()));
        }
    }

    /**
     * Get latest sensor readings
     */
    @GetMapping("/sensor-data/latest")
    public ResponseEntity<Map<String, Object>> getLatestSensorReadings(
            @RequestParam(required = false) String manufacturerId,
            @RequestParam(required = false) String factoryId,
            @RequestParam(required = false) String plcId) {

        try {
            List<Map<String, Object>> data = mcpServer.getLatestSensorReadings(manufacturerId, factoryId, plcId);

            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "count", data.size(),
                    "data", data));
        } catch (Exception e) {
            log.error("Error getting latest sensor readings", e);
            return ResponseEntity.badRequest().body(Map.of(
                    "success", false,
                    "error", e.getMessage()));
        }
    }

    /**
     * Get sensor statistics
     */
    @GetMapping("/sensor-data/statistics")
    public ResponseEntity<Map<String, Object>> getSensorStatistics(
            @RequestParam String sensorId,
            @RequestParam String startTime,
            @RequestParam String endTime) {

        try {
            Map<String, Object> stats = mcpServer.getSensorStatistics(sensorId, startTime, endTime);

            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "data", stats));
        } catch (Exception e) {
            log.error("Error getting sensor statistics", e);
            return ResponseEntity.badRequest().body(Map.of(
                    "success", false,
                    "error", e.getMessage()));
        }
    }

    /**
     * Get anomalies for a sensor
     */
    @GetMapping("/sensor-data/anomalies")
    public ResponseEntity<Map<String, Object>> getAnomalies(
            @RequestParam String sensorId,
            @RequestParam String startTime,
            @RequestParam String endTime,
            @RequestParam(required = false, defaultValue = "3.0") double threshold) {

        try {
            List<Map<String, Object>> anomalies = mcpServer.getAnomalies(sensorId, startTime, endTime, threshold);

            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "count", anomalies.size(),
                    "data", anomalies));
        } catch (Exception e) {
            log.error("Error getting anomalies", e);
            return ResponseEntity.badRequest().body(Map.of(
                    "success", false,
                    "error", e.getMessage()));
        }
    }

    /**
     * Get time-series aggregated data
     */
    @GetMapping("/sensor-data/timeseries")
    public ResponseEntity<Map<String, Object>> getTimeSeriesAggregation(
            @RequestParam String sensorId,
            @RequestParam String startTime,
            @RequestParam String endTime,
            @RequestParam(required = false, defaultValue = "1 hour") String interval) {

        try {
            List<Map<String, Object>> timeseries = mcpServer.getTimeSeriesAggregation(
                    sensorId, startTime, endTime, interval);

            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "count", timeseries.size(),
                    "data", timeseries));
        } catch (Exception e) {
            log.error("Error getting time-series aggregation", e);
            return ResponseEntity.badRequest().body(Map.of(
                    "success", false,
                    "error", e.getMessage()));
        }
    }

    /**
     * Get all manufacturers
     */
    @GetMapping("/manufacturers")
    public ResponseEntity<Map<String, Object>> getManufacturers() {
        try {
            List<Map<String, Object>> manufacturers = mcpServer.getManufacturers();

            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "count", manufacturers.size(),
                    "data", manufacturers));
        } catch (Exception e) {
            log.error("Error getting manufacturers", e);
            return ResponseEntity.badRequest().body(Map.of(
                    "success", false,
                    "error", e.getMessage()));
        }
    }

    /**
     * Get factories for a manufacturer
     */
    @GetMapping("/factories")
    public ResponseEntity<Map<String, Object>> getFactories(
            @RequestParam(required = false) String manufacturerId) {

        try {
            List<Map<String, Object>> factories = mcpServer.getFactories(manufacturerId);

            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "count", factories.size(),
                    "data", factories));
        } catch (Exception e) {
            log.error("Error getting factories", e);
            return ResponseEntity.badRequest().body(Map.of(
                    "success", false,
                    "error", e.getMessage()));
        }
    }

    /**
     * Get PLCs for a factory
     */
    @GetMapping("/plcs")
    public ResponseEntity<Map<String, Object>> getPLCs(@RequestParam String factoryId) {
        try {
            List<Map<String, Object>> plcs = mcpServer.getPLCs(factoryId);

            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "count", plcs.size(),
                    "data", plcs));
        } catch (Exception e) {
            log.error("Error getting PLCs", e);
            return ResponseEntity.badRequest().body(Map.of(
                    "success", false,
                    "error", e.getMessage()));
        }
    }

    /**
     * Get sensors for a PLC
     */
    @GetMapping("/sensors")
    public ResponseEntity<Map<String, Object>> getSensors(@RequestParam String plcId) {
        try {
            List<Map<String, Object>> sensors = mcpServer.getSensors(plcId);

            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "count", sensors.size(),
                    "data", sensors));
        } catch (Exception e) {
            log.error("Error getting sensors", e);
            return ResponseEntity.badRequest().body(Map.of(
                    "success", false,
                    "error", e.getMessage()));
        }
    }

    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        return ResponseEntity.ok(Map.of(
                "status", "healthy",
                "service", "TimescaleDB MCP Server",
                "timestamp", System.currentTimeMillis()));
    }
}
