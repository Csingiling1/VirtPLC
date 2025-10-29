package com.virtplc.service;

import java.util.Map;

/**
 * Interface for data source services.
 * Allows easy switching between simulator and real PLC.
 */
public interface DataSourceService {
    
    /**
     * Get latest sensor data from the data source.
     * @return Map of sensor data
     */
    Map<String, Object> getLatestSensorData();
    
    /**
     * Check if the data source is available.
     * @return true if available, false otherwise
     */
    boolean isAvailable();
    
    /**
     * Get the name of the data source.
     * @return data source name
     */
    String getDataSourceName();
}
