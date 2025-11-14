package com.virtplc.mcp;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.virtplc.repository.SensorDataRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import java.util.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * TimescaleDB MCP (Model Context Protocol) Server
 * Provides time-series data querying capabilities for AI services
 */
@Service
@ConditionalOnProperty(name = "mcp.enabled", havingValue = "true")
@RequiredArgsConstructor
@Slf4j
public class TimescaleMCPServer {

    private final JdbcTemplate jdbcTemplate;
    private final ObjectMapper objectMapper;

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

        StringBuilder sql = new StringBuilder(
                "SELECT timestamp, tenant_id, manufacturer_id, factory_id, plc_id, sensor_id, value, unit " +
                        "FROM telemetry_data WHERE 1=1");

        List<Object> params = new ArrayList<>();

        if (startTime != null && !startTime.isEmpty()) {
            sql.append(" AND timestamp >= ?");
            params.add(LocalDateTime.parse(startTime, DateTimeFormatter.ISO_DATE_TIME));
        }

        if (endTime != null && !endTime.isEmpty()) {
            sql.append(" AND timestamp <= ?");
            params.add(LocalDateTime.parse(endTime, DateTimeFormatter.ISO_DATE_TIME));
        }

        if (manufacturerId != null && !manufacturerId.isEmpty()) {
            sql.append(" AND manufacturer_id = ?");
            params.add(manufacturerId);
        }

        if (factoryId != null && !factoryId.isEmpty()) {
            sql.append(" AND factory_id = ?");
            params.add(factoryId);
        }

        if (plcId != null && !plcId.isEmpty()) {
            sql.append(" AND plc_id = ?");
            params.add(plcId);
        }

        if (sensorId != null && !sensorId.isEmpty()) {
            sql.append(" AND sensor_id = ?");
            params.add(sensorId);
        }

        sql.append(" ORDER BY timestamp DESC LIMIT 1000");

        return jdbcTemplate.queryForList(sql.toString(), params.toArray());
    }

    /**
     * Get latest sensor readings
     */
    public List<Map<String, Object>> getLatestSensorReadings(String manufacturerId, String factoryId, String plcId) {
        StringBuilder sql = new StringBuilder(
                "SELECT DISTINCT ON (sensor_id) sensor_id, timestamp, value, unit, manufacturer_id, factory_id, plc_id "
                        +
                        "FROM telemetry_data WHERE 1=1");

        List<Object> params = new ArrayList<>();

        if (manufacturerId != null && !manufacturerId.isEmpty()) {
            sql.append(" AND manufacturer_id = ?");
            params.add(manufacturerId);
        }

        if (factoryId != null && !factoryId.isEmpty()) {
            sql.append(" AND factory_id = ?");
            params.add(factoryId);
        }

        if (plcId != null && !plcId.isEmpty()) {
            sql.append(" AND plc_id = ?");
            params.add(plcId);
        }

        sql.append(" ORDER BY sensor_id, timestamp DESC");

        return jdbcTemplate.queryForList(sql.toString(), params.toArray());
    }

    /**
     * Get sensor statistics (avg, min, max, stddev)
     */
    public Map<String, Object> getSensorStatistics(String sensorId, String startTime, String endTime) {
        String sql = "SELECT " +
                "AVG(value) as avg_value, " +
                "MIN(value) as min_value, " +
                "MAX(value) as max_value, " +
                "STDDEV(value) as stddev_value, " +
                "COUNT(*) as count " +
                "FROM telemetry_data " +
                "WHERE sensor_id = ? " +
                "AND timestamp >= ? " +
                "AND timestamp <= ?";

        List<Map<String, Object>> result = jdbcTemplate.queryForList(sql,
                sensorId,
                LocalDateTime.parse(startTime, DateTimeFormatter.ISO_DATE_TIME),
                LocalDateTime.parse(endTime, DateTimeFormatter.ISO_DATE_TIME));

        return result.isEmpty() ? new HashMap<>() : result.get(0);
    }

    /**
     * Get anomalies (values that are X standard deviations away from mean)
     */
    public List<Map<String, Object>> getAnomalies(String sensorId, String startTime, String endTime,
            double threshold) {
        String sql = "WITH stats AS (" +
                "  SELECT AVG(value) as mean, STDDEV(value) as stddev " +
                "  FROM telemetry_data " +
                "  WHERE sensor_id = ? " +
                "  AND timestamp >= ? " +
                "  AND timestamp <= ?" +
                ") " +
                "SELECT t.timestamp, t.value, t.sensor_id, t.plc_id, t.factory_id, t.manufacturer_id, " +
                "  ABS(t.value - s.mean) / NULLIF(s.stddev, 0) as z_score " +
                "FROM telemetry_data t, stats s " +
                "WHERE t.sensor_id = ? " +
                "AND t.timestamp >= ? " +
                "AND t.timestamp <= ? " +
                "AND ABS(t.value - s.mean) / NULLIF(s.stddev, 0) > ? " +
                "ORDER BY timestamp DESC";

        return jdbcTemplate.queryForList(sql,
                sensorId,
                LocalDateTime.parse(startTime, DateTimeFormatter.ISO_DATE_TIME),
                LocalDateTime.parse(endTime, DateTimeFormatter.ISO_DATE_TIME),
                sensorId,
                LocalDateTime.parse(startTime, DateTimeFormatter.ISO_DATE_TIME),
                LocalDateTime.parse(endTime, DateTimeFormatter.ISO_DATE_TIME),
                threshold);
    }

    /**
     * Get time-series aggregation (using TimescaleDB's time_bucket function)
     */
    public List<Map<String, Object>> getTimeSeriesAggregation(
            String sensorId,
            String startTime,
            String endTime,
            String interval) {

        // Default interval is 1 hour if not specified
        String bucketInterval = (interval != null && !interval.isEmpty()) ? interval : "1 hour";

        String sql = "SELECT " +
                "time_bucket('" + bucketInterval + "', timestamp) as bucket, " +
                "AVG(value) as avg_value, " +
                "MIN(value) as min_value, " +
                "MAX(value) as max_value, " +
                "COUNT(*) as count " +
                "FROM telemetry_data " +
                "WHERE sensor_id = ? " +
                "AND timestamp >= ? " +
                "AND timestamp <= ? " +
                "GROUP BY bucket " +
                "ORDER BY bucket DESC";

        return jdbcTemplate.queryForList(sql,
                sensorId,
                LocalDateTime.parse(startTime, DateTimeFormatter.ISO_DATE_TIME),
                LocalDateTime.parse(endTime, DateTimeFormatter.ISO_DATE_TIME));
    }

    /**
     * Get all manufacturers
     */
    public List<Map<String, Object>> getManufacturers() {
        return jdbcTemplate.queryForList(
                "SELECT id, manufacturer_id, name, company_id, is_active FROM manufacturers WHERE is_active = true");
    }

    /**
     * Get all factories for a manufacturer
     */
    public List<Map<String, Object>> getFactories(String manufacturerId) {
        if (manufacturerId != null && !manufacturerId.isEmpty()) {
            return jdbcTemplate.queryForList(
                    "SELECT id, factory_id, name, manufacturer_id FROM factories WHERE manufacturer_id = (SELECT id FROM manufacturers WHERE manufacturer_id = ?)",
                    manufacturerId);
        } else {
            return jdbcTemplate.queryForList(
                    "SELECT id, factory_id, name, manufacturer_id FROM factories");
        }
    }

    /**
     * Get all PLCs for a factory
     */
    public List<Map<String, Object>> getPLCs(String factoryId) {
        return jdbcTemplate.queryForList(
                "SELECT id, plc_id, name, factory_id FROM plcs WHERE factory_id = (SELECT id FROM factories WHERE factory_id = ?)",
                factoryId);
    }

    /**
     * Get all sensors for a PLC
     */
    public List<Map<String, Object>> getSensors(String plcId) {
        return jdbcTemplate.queryForList(
                "SELECT id, sensor_id, name, unit, plc_id FROM sensors WHERE plc_id = (SELECT id FROM plcs WHERE plc_id = ?)",
                plcId);
    }
}
