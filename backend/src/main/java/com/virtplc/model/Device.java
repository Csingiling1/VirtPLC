package com.virtplc.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Device entity representing any type of industrial device.
 * Uses JPA for dynamic device configuration and mapping.
 */
@Entity
@Table(name = "devices")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Device {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "device_id", unique = true, nullable = false)
    private String deviceId;

    @Column(name = "device_name", nullable = false)
    private String deviceName;

    @Column(name = "device_type", nullable = false)
    private String deviceType; // motor, conveyor, placer, sensor, etc.

    @Column(name = "manufacturer_id")
    private String manufacturerId;

    @Column(name = "factory_id")
    private String factoryId;

    @Column(name = "plc_id")
    private String plcId;

    @Column(name = "description")
    private String description;

    @Column(name = "is_active", nullable = false)
    @Builder.Default
    private Boolean isActive = true;

    @Column(name = "data_timeout_seconds", nullable = false)
    @Builder.Default
    private Integer dataTimeoutSeconds = 300; // 5 minutes default

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