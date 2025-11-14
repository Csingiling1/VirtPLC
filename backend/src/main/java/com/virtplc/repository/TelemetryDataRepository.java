package com.virtplc.repository;

import com.virtplc.model.TelemetryDataEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;

/**
 * Repository for telemetry data stored in TimescaleDB.
 * Provides time-series optimized queries for multi-tenant telemetry data.
 */
@Repository
public interface TelemetryDataRepository extends JpaRepository<TelemetryDataEntity, Long> {

    /**
     * Find telemetry data for a specific tenant within a timestamp range.
     */
    List<TelemetryDataEntity> findByTenantIdAndTimestampBetween(
            String tenantId, Instant startTime, Instant endTime);

    /**
     * Find telemetry data for a specific tenant and manufacturer within a timestamp
     * range.
     */
    List<TelemetryDataEntity> findByTenantIdAndManufacturerIdAndTimestampBetween(
            String tenantId, String manufacturerId, Instant startTime, Instant endTime);

    /**
     * Find telemetry data for a specific tenant, manufacturer, and factory within a
     * timestamp range.
     */
    List<TelemetryDataEntity> findByTenantIdAndManufacturerIdAndFactoryIdAndTimestampBetween(
            String tenantId, String manufacturerId, String factoryId, Instant startTime, Instant endTime);

    /**
     * Find telemetry data for a specific PLC within a timestamp range.
     */
    List<TelemetryDataEntity> findByTenantIdAndManufacturerIdAndFactoryIdAndPlcIdAndTimestampBetween(
            String tenantId, String manufacturerId, String factoryId, String plcId, Instant startTime, Instant endTime);

    /**
     * Find telemetry data for a specific sensor within a timestamp range.
     */
    List<TelemetryDataEntity> findByTenantIdAndManufacturerIdAndFactoryIdAndPlcIdAndSensorIdAndTimestampBetween(
            String tenantId, String manufacturerId, String factoryId, String plcId, String sensorId,
            Instant startTime, Instant endTime);

    /**
     * Get latest telemetry data for a specific tenant.
     */
    @Query("SELECT t FROM TelemetryDataEntity t WHERE t.tenantId = :tenantId ORDER BY t.timestamp DESC LIMIT :limit")
    List<TelemetryDataEntity> findLatestByTenantId(@Param("tenantId") String tenantId, @Param("limit") int limit);

    /**
     * Count telemetry readings for a tenant within a time range.
     */
    long countByTenantIdAndTimestampBetween(String tenantId, Instant startTime, Instant endTime);

    /**
     * Get distinct sensor IDs for a tenant.
     */
    @Query("SELECT DISTINCT t.sensorId FROM TelemetryDataEntity t WHERE t.tenantId = :tenantId")
    List<String> findDistinctSensorIdsByTenantId(@Param("tenantId") String tenantId);
}