package com.virtplc.mcp;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import java.util.*;

/**
 * TimescaleDB MCP (Model Context Protocol) Server
 * Provides time-series data querying capabilities for AI services
 * Now delegates to external MCP client
 */
@Service
@ConditionalOnProperty(name = "mcp.enabled", havingValue = "true")
@RequiredArgsConstructor
@Slf4j
public class TimescaleMCPServer {

    private final MCPClient mcpClient;

    @PostConstruct
    public void init() {
        log.info("TimescaleDB MCP Server initialized");
    }

    /**
     * Query sensor data by time range
     */
    public List<Map<String, Object>> querySensorDataByTimeRange(
            String startTime,
            String endTime,
            String manufacturerId,
            String factoryId,
            String plcId,
            String sensorId) {

        return mcpClient.querySensorDataByTimeRange(startTime, endTime, manufacturerId, factoryId, plcId, sensorId);
    }

    /**
     * Get all factories for a manufacturer
     */
    public List<Map<String, Object>> getFactories(String manufacturerId) {
        return mcpClient.getFactories(manufacturerId);
    }

    /**
     * Get all PLCs for a factory
     */
    public List<Map<String, Object>> getPLCs(String factoryId) {
        return mcpClient.getPLCs(factoryId);
    }

    /**
     * Get all sensors for a PLC
     */
    public List<Map<String, Object>> getSensors(String plcId) {
        return mcpClient.getSensors(plcId);
    }

    /**
     * Get latest sensor readings
     */
    public List<Map<String, Object>> getLatestSensorReadings(String manufacturerId, String factoryId, String plcId) {
        return mcpClient.getLatestSensorReadings(manufacturerId, factoryId, plcId);
    }

    /**
     * Get sensor statistics (avg, min, max, stddev)
     */
    public Map<String, Object> getSensorStatistics(String sensorId, String startTime, String endTime) {
        return mcpClient.getSensorStatistics(sensorId, startTime, endTime);
    }

    /**
     * Get anomalies (values that are X standard deviations away from mean)
     */
    public List<Map<String, Object>> getAnomalies(String sensorId, String startTime, String endTime, double threshold) {
        return mcpClient.getAnomalies(sensorId, startTime, endTime, threshold);
    }

    /**
     * Get time-series aggregation (using TimescaleDB's time_bucket function)
     */
    public List<Map<String, Object>> getTimeSeriesAggregation(String sensorId, String startTime, String endTime,
            String interval) {
        return mcpClient.getTimeSeriesAggregation(sensorId, startTime, endTime, interval);
    }

    /**
     * Get all PLCs (devices)
     */
    public List<Map<String, Object>> getAllPLCs() {
        return mcpClient.getAllPLCs();
    }

    /**
     * Get all sensors (signals)
     */
    public List<Map<String, Object>> getAllSensors() {
        return mcpClient.getAllSensors();
    }

    /**
     * Get all manufacturers
     */
    public List<Map<String, Object>> getManufacturers() {
        return mcpClient.getManufacturers();
    }
}
