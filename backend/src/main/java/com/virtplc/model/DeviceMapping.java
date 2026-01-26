package com.virtplc.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Device mapping configuration entity.
 * Defines how device data should be mapped to SensorData fields.
 */
@Entity
@Table(name = "device_mappings")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DeviceMapping {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "device_id", nullable = false)
    private Device device;

    @Column(name = "field_name", nullable = false)
    private String fieldName; // e.g., "motor1Speed", "conveyor1Rpm", "temperature"

    @Column(name = "field_type", nullable = false)
    private String fieldType; // "numeric", "boolean", "string"

    @Column(name = "value_path")
    private String valuePath; // JSON path to extract value from signal_config

    @Column(name = "status_path")
    private String statusPath; // JSON path to extract status from signal_config

    @Column(name = "unit")
    private String unit; // measurement unit

    @Column(name = "multiplier", nullable = false)
    @Builder.Default
    private Double multiplier = 1.0; // value multiplier for scaling

    @Column(name = "value_offset", nullable = false)
    @Builder.Default
    private Double offset = 0.0; // value offset

    @Column(name = "is_active", nullable = false)
    @Builder.Default
    private Boolean isActive = true;

    @Column(name = "created_at", nullable = false)
    private java.time.LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private java.time.LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = java.time.LocalDateTime.now();
        updatedAt = java.time.LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = java.time.LocalDateTime.now();
    }
}