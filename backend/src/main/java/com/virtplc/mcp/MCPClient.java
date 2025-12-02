package com.virtplc.mcp;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

/**
 * MCP Client for communicating with external db-mcp-server
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class MCPClient {

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    @Value("${mcp.server.url:http://db-mcp-server:9092}")
    private String mcpServerUrl;

    private int requestId = 1;

    /**
     * Execute SQL query using MCP server
     */
    public List<Map<String, Object>> executeQuery(String sql) {
        try {
            Map<String, Object> request = Map.of(
                    "jsonrpc", "2.0",
                    "id", requestId++,
                    "method", "tools/call",
                    "params", Map.of(
                            "name", "query_timescale",
                            "arguments", Map.of("query", sql)));

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);

            ResponseEntity<String> response = restTemplate.postForEntity(
                    mcpServerUrl + "/jsonrpc", entity, String.class);

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                JsonNode responseJson = objectMapper.readTree(response.getBody());
                if (responseJson.has("result") && responseJson.get("result").has("content")) {
                    JsonNode content = responseJson.get("result").get("content");
                    if (content.isArray() && content.size() > 0) {
                        JsonNode firstContent = content.get(0);
                        if (firstContent.has("text")) {
                            String text = firstContent.get("text").asText();
                            log.debug("Raw MCP response text: {}", text);
                            // Handle MCP server returning nested map structure
                            if (text.startsWith("map[content:[map[text:")) {
                                // Extract the actual SQL results from the nested structure
                                int textStart = text.indexOf("text:") + 5;
                                int textEnd = text.lastIndexOf("]]]") - 1;
                                if (textStart > 0 && textEnd > textStart) {
                                    text = text.substring(textStart, textEnd);
                                    log.debug("Extracted SQL text: {}", text);
                                }
                            }
                            // Parse the SQL result text format
                            return parseSqlResultText(text);
                        }
                    }
                }
            }
            log.warn("Failed to execute query via MCP: {}", response.getBody());
            return Collections.emptyList();
        } catch (Exception e) {
            log.error("Error executing query via MCP", e);
            return Collections.emptyList();
        }
    }

    /**
     * Query sensor data by time range
     */
    public List<Map<String, Object>> querySensorDataByTimeRange(
            String startTime, String endTime, String manufacturerId,
            String factoryId, String plcId, String sensorId) {

        StringBuilder sql = new StringBuilder(
                "SELECT timestamp, tenant_id, manufacturer_id, factory_id, plc_id, sensor_id, value, unit " +
                        "FROM telemetry_data WHERE 1=1");

        List<String> conditions = new ArrayList<>();
        if (startTime != null && !startTime.isEmpty()) {
            conditions.add("timestamp >= '" + startTime + "'");
        }
        if (endTime != null && !endTime.isEmpty()) {
            conditions.add("timestamp <= '" + endTime + "'");
        }
        if (manufacturerId != null && !manufacturerId.isEmpty()) {
            conditions.add("manufacturer_id = '" + manufacturerId + "'");
        }
        if (factoryId != null && !factoryId.isEmpty()) {
            conditions.add("factory_id = '" + factoryId + "'");
        }
        if (plcId != null && !plcId.isEmpty()) {
            conditions.add("plc_id = '" + plcId + "'");
        }
        if (sensorId != null && !sensorId.isEmpty()) {
            conditions.add("sensor_id = '" + sensorId + "'");
        }

        if (!conditions.isEmpty()) {
            sql.append(" AND ").append(String.join(" AND ", conditions));
        }

        sql.append(" ORDER BY timestamp DESC LIMIT 1000");

        return executeQuery(sql.toString());
    }

    /**
     * Get all factories
     */
    public List<Map<String, Object>> getFactories(String manufacturerId) {
        String sql;
        if (manufacturerId != null && !manufacturerId.isEmpty()) {
            sql = "SELECT id, factory_id, name, manufacturer_id FROM factories WHERE manufacturer_id = (SELECT id FROM manufacturers WHERE manufacturer_id = '"
                    + manufacturerId + "')";
        } else {
            sql = "SELECT id, factory_id, name, manufacturer_id FROM factories";
        }
        return executeQuery(sql);
    }

    /**
     * Get all PLCs for a factory
     */
    public List<Map<String, Object>> getPLCs(String factoryId) {
        String sql = "SELECT id, plc_id, name, factory_id FROM plcs WHERE factory_id = (SELECT id FROM factories WHERE factory_id = '"
                + factoryId + "')";
        return executeQuery(sql);
    }

    /**
     * Get all sensors for a PLC
     */
    public List<Map<String, Object>> getSensors(String plcId) {
        String sql = "SELECT id, sensor_id, name, unit, plc_id FROM sensors WHERE plc_id = (SELECT id FROM plcs WHERE plc_id = '"
                + plcId + "')";
        return executeQuery(sql);
    }

    /**
     * Get latest sensor readings
     */
    public List<Map<String, Object>> getLatestSensorReadings(String manufacturerId, String factoryId, String plcId) {
        String sql = "SELECT DISTINCT ON (sensor_id) sensor_id, timestamp, value, unit, manufacturer_id, factory_id, plc_id FROM telemetry_data WHERE 1=1";
        if (manufacturerId != null && !manufacturerId.isEmpty()) {
            sql += " AND manufacturer_id = '" + manufacturerId + "'";
        }
        if (factoryId != null && !factoryId.isEmpty()) {
            sql += " AND factory_id = '" + factoryId + "'";
        }
        if (plcId != null && !plcId.isEmpty()) {
            sql += " AND plc_id = '" + plcId + "'";
        }
        sql += " ORDER BY sensor_id, timestamp DESC";
        return executeQuery(sql);
    }

    /**
     * Get sensor statistics (avg, min, max, stddev)
     */
    public Map<String, Object> getSensorStatistics(String sensorId, String startTime, String endTime) {
        String sql = "SELECT AVG(value) as avg_value, MIN(value) as min_value, MAX(value) as max_value, STDDEV(value) as stddev_value, COUNT(*) as count FROM telemetry_data WHERE sensor_id = '"
                + sensorId + "' AND timestamp >= '" + startTime + "' AND timestamp <= '" + endTime + "'";
        List<Map<String, Object>> result = executeQuery(sql);
        return result.isEmpty() ? new HashMap<>() : result.get(0);
    }

    /**
     * Get anomalies (values that are X standard deviations away from mean)
     */
    public List<Map<String, Object>> getAnomalies(String sensorId, String startTime, String endTime, double threshold) {
        String sql = "WITH stats AS (SELECT AVG(value) as mean, STDDEV(value) as stddev FROM telemetry_data WHERE sensor_id = '"
                + sensorId + "' AND timestamp >= '" + startTime + "' AND timestamp <= '" + endTime
                + "') SELECT t.timestamp, t.value, t.sensor_id, t.plc_id, t.factory_id, t.manufacturer_id, ABS(t.value - s.mean) / NULLIF(s.stddev, 0) as z_score FROM telemetry_data t, stats s WHERE t.sensor_id = '"
                + sensorId + "' AND t.timestamp >= '" + startTime + "' AND t.timestamp <= '" + endTime
                + "' AND ABS(t.value - s.mean) / NULLIF(s.stddev, 0) > " + threshold + " ORDER BY timestamp DESC";
        return executeQuery(sql);
    }

    /**
     * Get time-series aggregation (using TimescaleDB's time_bucket function)
     */
    public List<Map<String, Object>> getTimeSeriesAggregation(String sensorId, String startTime, String endTime,
            String interval) {
        String bucketInterval = (interval != null && !interval.isEmpty()) ? interval : "1 hour";
        String sql = "SELECT time_bucket('" + bucketInterval
                + "', timestamp) as bucket, AVG(value) as avg_value, MIN(value) as min_value, MAX(value) as max_value, COUNT(*) as count FROM telemetry_data WHERE sensor_id = '"
                + sensorId + "' AND timestamp >= '" + startTime + "' AND timestamp <= '" + endTime
                + "' GROUP BY bucket ORDER BY bucket DESC";
        return executeQuery(sql);
    }

    /**
     * Get all PLCs (devices)
     */
    public List<Map<String, Object>> getAllPLCs() {
        String sql = "SELECT id, plc_id, name, factory_id FROM plcs WHERE is_active = true";
        return executeQuery(sql);
    }

    /**
     * Get all sensors (signals)
     */
    public List<Map<String, Object>> getAllSensors() {
        String sql = "SELECT id, sensor_id, name, signal_unit as unit, plc_id FROM sensors WHERE is_active = true";
        return executeQuery(sql);
    }

    /**
     * Parse SQL result text format into list of maps
     */
    private List<Map<String, Object>> parseSqlResultText(String text) {
        List<Map<String, Object>> results = new ArrayList<>();
        log.debug("Parsing SQL text: {}", text);

        try {
            String[] lines = text.split("\n");
            if (lines.length < 3) {
                return results; // Not enough lines for header + separator + data
            }

            // Find the header line (skip "Results:" and empty lines)
            int headerIndex = 0;
            if (lines[0].trim().equals("Results:")) {
                headerIndex = 1;
            }

            // Skip empty lines to find the actual header
            while (headerIndex < lines.length && lines[headerIndex].trim().isEmpty()) {
                headerIndex++;
            }

            if (headerIndex >= lines.length) {
                return results;
            }

            String headerLine = lines[headerIndex].trim();

            // Parse headers by splitting on tabs
            String[] headers = headerLine.split("\t");

            // Find the separator line
            int separatorIndex = headerIndex + 1;
            while (separatorIndex < lines.length && !lines[separatorIndex].trim().matches("-+")) {
                separatorIndex++;
            }

            if (separatorIndex >= lines.length) {
                return results;
            }

            // Parse data rows
            int dataStartIndex = separatorIndex + 1;
            for (int i = dataStartIndex; i < lines.length; i++) {
                String line = lines[i].trim();
                if (line.isEmpty() || line.startsWith("Total rows:")) {
                    break; // End of data
                }

                log.debug("Parsing data line: {}", line);
                String[] values = line.split("\t");
                if (values.length >= headers.length) {
                    Map<String, Object> row = new HashMap<>();
                    for (int j = 0; j < headers.length && j < values.length; j++) {
                        String header = headers[j].toLowerCase();
                        String value = values[j];

                        // Try to parse as number if possible
                        try {
                            if (value.matches("\\d+")) {
                                row.put(header, Integer.parseInt(value));
                            } else if (value.matches("\\d+\\.\\d+")) {
                                row.put(header, Double.parseDouble(value));
                            } else {
                                row.put(header, value);
                            }
                        } catch (NumberFormatException e) {
                            row.put(header, value);
                        }
                    }
                    results.add(row);
                }
            }
        } catch (Exception e) {
            log.error("Failed to parse SQL result text: {}", text, e);
        }

        return results;
    }

    /**
     * Get all manufacturers
     */
    public List<Map<String, Object>> getManufacturers() {
        String sql = "SELECT id, manufacturer_id, name, company_id, is_active FROM manufacturers WHERE is_active = true";
        return executeQuery(sql);
    }
}