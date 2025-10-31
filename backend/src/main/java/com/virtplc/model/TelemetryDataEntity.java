package com.virtplc.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

/**
 * JPA entity for storing telemetry data in TimescaleDB.
 * Uses time-series optimized storage for high-throughput ingestion.
 */
@Entity
@Table(name = "telemetry_data")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TelemetryDataEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "tenant_id", nullable = false)
    private String tenantId;

    @Column(name = "manufacturer_id", nullable = false)
    private String manufacturerId;

    @Column(name = "factory_id", nullable = false)
    private String factoryId;

    @Column(name = "plc_id", nullable = false)
    private String plcId;

    @Column(name = "sensor_id", nullable = false)
    private String sensorId;

    @Column(name = "value", nullable = false)
    private Double value;

    @Column(name = "unit")
    private String unit;

    @Column(name = "timestamp", nullable = false)
    private Instant timestamp;

    @Column(name = "metadata", columnDefinition = "TEXT")
    private String metadata;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    @PrePersist
    protected void onCreate() {
        if (createdAt == null) {
            createdAt = Instant.now();
        }
    }
}