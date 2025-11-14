package com.virtplc.service;

import com.virtplc.model.TelemetryData;
import com.virtplc.model.TelemetryDataEntity;
import com.virtplc.repository.TelemetryDataRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.concurrent.CompletableFuture;

/**
 * Service for ingesting and processing telemetry data from collectors.
 * Handles validation, transformation, and storage of multi-tenant telemetry data.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class TelemetryIngestionService {

    private final TelemetryDataRepository telemetryDataRepository;

    /**
     * Ingests telemetry data from a collector.
     * Validates the data and stores it asynchronously for high throughput.
     */
    @Transactional
    public CompletableFuture<Void> ingestTelemetry(TelemetryData telemetryData) {
        return CompletableFuture.runAsync(() -> {
            try {
                // Validate the telemetry data
                if (!telemetryData.isValid()) {
                    log.warn("Invalid telemetry data received: {}", telemetryData);
                    throw new IllegalArgumentException("Invalid telemetry data: missing required fields");
                }

                // Convert domain model to entity
                TelemetryDataEntity entity = TelemetryDataEntity.builder()
                        .tenantId(telemetryData.getTenantId())
                        .manufacturerId(telemetryData.getManufacturerId())
                        .factoryId(telemetryData.getFactoryId())
                        .plcId(telemetryData.getPlcId())
                        .sensorId(telemetryData.getSensorId())
                        .value(telemetryData.getValue())
                        .unit(telemetryData.getUnit())
                        .timestamp(telemetryData.getTimestamp())
                        .metadata(telemetryData.getMetadata())
                        .createdAt(telemetryData.getTimestamp())
                        .build();

                // Save to database
                telemetryDataRepository.save(entity);

                log.debug("Successfully ingested telemetry data: {}", telemetryData.getCompositeId());

            } catch (Exception e) {
                log.error("Failed to ingest telemetry data: {}", e.getMessage(), e);
                throw new RuntimeException("Failed to ingest telemetry data", e);
            }
        });
    }

    /**
     * Batch ingest multiple telemetry readings.
     * More efficient for high-volume data streams.
     */
    @Transactional
    public CompletableFuture<Void> ingestTelemetryBatch(Iterable<TelemetryData> telemetryBatch) {
        return CompletableFuture.runAsync(() -> {
            try {
                int count = 0;
                for (TelemetryData telemetryData : telemetryBatch) {
                    if (telemetryData.isValid()) {
                        TelemetryDataEntity entity = TelemetryDataEntity.builder()
                                .tenantId(telemetryData.getTenantId())
                                .manufacturerId(telemetryData.getManufacturerId())
                                .factoryId(telemetryData.getFactoryId())
                                .plcId(telemetryData.getPlcId())
                                .sensorId(telemetryData.getSensorId())
                                .value(telemetryData.getValue())
                                .unit(telemetryData.getUnit())
                                .timestamp(telemetryData.getTimestamp())
                                .metadata(telemetryData.getMetadata())
                                .createdAt(telemetryData.getTimestamp())
                                .build();

                        telemetryDataRepository.save(entity);
                        count++;
                    } else {
                        log.warn("Skipping invalid telemetry data in batch: {}", telemetryData);
                    }
                }

                log.info("Successfully ingested {} telemetry readings in batch", count);

            } catch (Exception e) {
                log.error("Failed to ingest telemetry batch: {}", e.getMessage(), e);
                throw new RuntimeException("Failed to ingest telemetry batch", e);
            }
        });
    }
}