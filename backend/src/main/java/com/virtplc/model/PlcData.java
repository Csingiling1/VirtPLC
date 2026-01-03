package com.virtplc.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * DTO for PLC data stored in TimescaleDB plc_data table.
 * Note: This table doesn't have a primary key - it's a time-series table.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PlcData {
    private LocalDateTime timestamp;
    private String deviceId;
    private String type;
    private JsonNode data; // JSONB column
    private JsonNode metadata; // JSONB column
    private Double rpm;
    private Double positionX;
    private Double positionY;
    private Boolean isOn;
    private Boolean inOperation;
}