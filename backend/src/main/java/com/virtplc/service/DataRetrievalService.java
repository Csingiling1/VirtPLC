package com.virtplc.service;

import com.virtplc.model.Company;
import com.virtplc.model.Manufacturer;
import com.virtplc.model.SensorData;

import java.util.List;

/**
 * Interface for data retrieval operations.
 * Follows Interface Segregation Principle by separating read operations.
 */
public interface DataRetrievalService {

    /**
     * Retrieves the latest sensor data for given manufacturers.
     */
    SensorData getLatestData(List<Manufacturer> manufacturers);

    /**
     * Retrieves historical data within a time range with pagination.
     */
    List<SensorData> getDataRange(List<Manufacturer> manufacturers, Long startTime, Long endTime, int page, int size);

    /**
     * Retrieves data for a specific device within a time range.
     */
    List<SensorData> getDeviceData(Company company, String deviceId, Long startTime, Long endTime);
}