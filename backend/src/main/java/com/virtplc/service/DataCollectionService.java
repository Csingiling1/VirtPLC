package com.virtplc.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

/**
 * Service for collecting sensor data from OPC UA server and storing in TimescaleDB.
 * Runs periodically to ensure continuous data collection.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DataCollectionService {

    private final DataService dataService;

    @Value("${opcua.collection.interval:2000}")
    private long collectionInterval;

    /**
     * Collect sensor data from OPC UA server every configured interval.
     * Default interval is 2 seconds.
     */
    @Scheduled(fixedRateString = "${opcua.collection.interval:2000}")
    public void collectSensorData() {
        try {
            log.debug("Collecting sensor data from OPC UA server");

            // Get latest data (this will read from OPC UA and persist to TimescaleDB)
            dataService.getLatestData();

            log.debug("Successfully collected and stored sensor data");

        } catch (Exception e) {
            log.error("Failed to collect sensor data", e);
        }
    }
}