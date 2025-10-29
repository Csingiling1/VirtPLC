package com.virtplc.service;

import com.virtplc.model.Company;
import com.virtplc.repository.CompanyRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * Service for collecting sensor data from OPC UA server and storing in
 * TimescaleDB.
 * Runs periodically to ensure continuous data collection.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DataCollectionService {

    private final DataService dataService;
    private final CompanyRepository companyRepository;

    @Value("${opcua.collection.interval:2000}")
    private long collectionInterval;

    /**
     * Collect sensor data from OPC UA server every configured interval.
     * Default interval is 2 seconds.
     * Collects data for all active companies.
     */
    @Scheduled(fixedRateString = "${opcua.collection.interval:2000}")
    public void collectSensorData() {
        try {
            log.debug("Collecting sensor data from OPC UA server for all companies");

            List<Company> companies = companyRepository.findAll().stream()
                    .filter(Company::isActive)
                    .toList();

            for (Company company : companies) {
                try {
                    // Get latest data for each company (this will read from OPC UA and persist to
                    // TimescaleDB)
                    dataService.getLatestData(company);
                    log.debug("Successfully collected and stored sensor data for company: {}", company.getName());
                } catch (Exception e) {
                    log.error("Failed to collect sensor data for company: {}", company.getName(), e);
                }
            }

        } catch (Exception e) {
            log.error("Failed to collect sensor data", e);
        }
    }
}