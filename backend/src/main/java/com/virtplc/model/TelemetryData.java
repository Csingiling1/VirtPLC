package com.virtplc.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

/**
 * Domain model for telemetry data received from collectors.
 * Represents sensor readings from PLCs in a multi-tenant factory environment.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TelemetryData {

    private String tenantId;
    private String manufacturerId;
    private String factoryId;
    private String plcId;
    private String sensorId;
    private Double value;
    private String unit;
    private Instant timestamp;
    private String metadata;

    /**
     * Creates a unique identifier for this telemetry reading
     */
    public String getCompositeId() {
        return String.format("%s-%s-%s-%s-%s-%d",
                tenantId, manufacturerId, factoryId, plcId, sensorId, timestamp.toEpochMilli());
    }

    /**
     * Validates that all required fields are present
     */
    public boolean isValid() {
        return tenantId != null && !tenantId.trim().isEmpty() &&
                manufacturerId != null && !manufacturerId.trim().isEmpty() &&
                factoryId != null && !factoryId.trim().isEmpty() &&
                plcId != null && !plcId.trim().isEmpty() &&
                sensorId != null && !sensorId.trim().isEmpty() &&
                value != null &&
                timestamp != null;
    }
}