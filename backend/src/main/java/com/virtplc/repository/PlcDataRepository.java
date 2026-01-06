package com.virtplc.repository;

import com.virtplc.model.PlcData;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

/**
 * Repository for PLC data stored in TimescaleDB.
 * Note: plc_data table doesn't have a primary key (time-series table).
 */
@Repository
public class PlcDataRepository {

    private final JdbcTemplate jdbcTemplate;
    private final ObjectMapper objectMapper;

    public PlcDataRepository(JdbcTemplate jdbcTemplate, ObjectMapper objectMapper) {
        this.jdbcTemplate = jdbcTemplate;
        this.objectMapper = objectMapper;
    }

    /**
     * Find PLC data within a timestamp range.
     */
    public List<PlcData> findByTimestampBetween(LocalDateTime startTime, LocalDateTime endTime) {
        String sql = """
                SELECT timestamp, device_id, type, data, metadata, rpm, position_x, position_y, is_on, in_operation
                FROM plc_data
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
                """;

        return jdbcTemplate.query(sql, new PlcDataRowMapper(), startTime, endTime);
    }

    /**
     * Find the latest PLC data for a device.
     */
    public PlcData findLatestByDeviceId(String deviceId) {
        String sql = """
                SELECT timestamp, device_id, type, data, metadata, rpm, position_x, position_y, is_on, in_operation
                FROM plc_data
                WHERE device_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
                """;

        List<PlcData> results = jdbcTemplate.query(sql, new PlcDataRowMapper(), deviceId);
        return results.isEmpty() ? null : results.get(0);
    }

    /**
     * Find all latest PLC data grouped by device_id.
     */
    @Cacheable(value = "devices", key = "'all-devices'")
    public List<PlcData> findLatestForAllDevices() {
        String sql = """
                SELECT DISTINCT ON (device_id) timestamp, device_id, type, data, metadata, rpm, position_x, position_y, is_on, in_operation
                FROM plc_data
                ORDER BY device_id, timestamp DESC
                """;

        return jdbcTemplate.query(sql, new PlcDataRowMapper());
    }

    /**
     * Get all distinct device IDs from plc_data table.
     */
    public List<String> findAllDistinctDeviceIds() {
        String sql = "SELECT DISTINCT device_id FROM plc_data ORDER BY device_id";
        return jdbcTemplate.queryForList(sql, String.class);
    }

    /**
     * Find latest sensor data grouped by device_id where type='sensor'.
     * Returns latest reading for each simulator sensor.
     */
    @Cacheable(value = "devices", key = "'sensors'")
    public List<PlcData> findLatestSensors() {
        String sql = """
                SELECT DISTINCT ON (device_id) timestamp, device_id, type, data, metadata, rpm, position_x, position_y, is_on, in_operation
                FROM plc_data
                WHERE type = 'sensor'
                ORDER BY device_id, timestamp DESC
                """;

        return jdbcTemplate.query(sql, new PlcDataRowMapper());
    }

    /**
     * Find latest UNREAL devices.
     */
    @Cacheable(value = "devices", key = "'unreal'")
    public List<PlcData> findLatestUnrealDevices() {
        String sql = """
                SELECT DISTINCT ON (device_id) timestamp, device_id, type, data, metadata, rpm, position_x, position_y, is_on, in_operation
                FROM plc_data
                WHERE type = 'UNREAL'
                ORDER BY device_id, timestamp DESC
                """;

        return jdbcTemplate.query(sql, new PlcDataRowMapper());
    }

    /**
     * Find historical data for a specific device within a time range.
     * Returns timestamp, deviceId, and value for charting.
     */
    @Cacheable(value = "history", key = "#deviceId + '-' + #startTimeMs + '-' + #endTimeMs")
    public List<Map<String, Object>> findDeviceHistory(String deviceId, Long startTimeMs, Long endTimeMs) {
        String sql = """
                SELECT
                    EXTRACT(EPOCH FROM timestamp) * 1000 as timestamp,
                    device_id,
                    COALESCE(rpm, position_x, position_y, 0.0) as value
                FROM plc_data
                WHERE device_id = ?
                  AND timestamp >= to_timestamp(? / 1000.0)
                  AND timestamp <= to_timestamp(? / 1000.0)
                ORDER BY timestamp ASC
                LIMIT 10000
                """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> {
            java.util.Map<String, Object> map = new java.util.HashMap<>();
            map.put("timestamp", rs.getLong("timestamp"));
            map.put("deviceId", rs.getString("device_id"));
            map.put("value", rs.getDouble("value"));
            return map;
        }, deviceId, startTimeMs, endTimeMs);
    }

    private class PlcDataRowMapper implements RowMapper<PlcData> {
        @Override
        public PlcData mapRow(ResultSet rs, int rowNum) throws SQLException {
            try {
                JsonNode dataNode = rs.getString("data") != null ? objectMapper.readTree(rs.getString("data")) : null;
                JsonNode metadataNode = rs.getString("metadata") != null
                        ? objectMapper.readTree(rs.getString("metadata"))
                        : null;

                return PlcData.builder()
                        .timestamp(rs.getTimestamp("timestamp").toLocalDateTime())
                        .deviceId(rs.getString("device_id"))
                        .type(rs.getString("type"))
                        .data(dataNode)
                        .metadata(metadataNode)
                        .rpm(rs.getDouble("rpm"))
                        .positionX(rs.getDouble("position_x"))
                        .positionY(rs.getDouble("position_y"))
                        .isOn(rs.getBoolean("is_on"))
                        .inOperation(rs.getBoolean("in_operation"))
                        .build();
            } catch (Exception e) {
                throw new SQLException("Failed to map PlcData row", e);
            }
        }
    }
}