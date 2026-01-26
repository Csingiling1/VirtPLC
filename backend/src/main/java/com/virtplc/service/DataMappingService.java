package com.virtplc.service;

import com.virtplc.model.PlcData;
import com.virtplc.model.SensorData;
import com.fasterxml.jackson.databind.JsonNode;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Interface for data mapping and transformation operations.
 * Follows Single Responsibility Principle by isolating mapping logic.
 */
public interface DataMappingService {

    /**
     * Maps PlcData to SensorData for a single record.
     */
    SensorData mapPlcDataToSensorData(PlcData plcData);

    /**
     * Maps a list of PlcData records to SensorData.
     */
    SensorData mapPlcDataListToSensorData(List<PlcData> plcDataList, LocalDateTime timestamp);

    /**
     * Extracts value from signal configuration JSON.
     */
    Double extractValueFromSignalConfig(JsonNode signalConfig);

    /**
     * Extracts boolean status from signal configuration JSON.
     */
    Boolean extractStatusFromSignalConfig(JsonNode signalConfig);

    /**
     * Maps device-specific data based on device ID.
     */
    void mapDeviceSpecificData(SensorData.SensorDataBuilder builder, String deviceId, JsonNode dataNode);
}