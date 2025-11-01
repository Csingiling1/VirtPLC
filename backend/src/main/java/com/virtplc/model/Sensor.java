package com.virtplc.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "sensors")
public class Sensor {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String sensorId;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private Boolean isActive = true;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "plc_id", nullable = false)
    private PLC plc;

    // Signal configuration embedded
    @Embedded
    @AttributeOverrides({
            @AttributeOverride(name = "name", column = @Column(name = "signal_name")),
            @AttributeOverride(name = "unit", column = @Column(name = "signal_unit")),
            @AttributeOverride(name = "value", column = @Column(name = "signal_value")),
            @AttributeOverride(name = "generator", column = @Column(name = "signal_generator")),
            @AttributeOverride(name = "isRunning", column = @Column(name = "signal_is_running")),
            @AttributeOverride(name = "minValue", column = @Column(name = "signal_min_value")),
            @AttributeOverride(name = "maxValue", column = @Column(name = "signal_max_value")),
            @AttributeOverride(name = "mean", column = @Column(name = "signal_mean")),
            @AttributeOverride(name = "stdDev", column = @Column(name = "signal_std_dev"))
    })
    private SignalConfig signalConfig;

    // Constructors
    public Sensor() {
    }

    public Sensor(String sensorId, String name, PLC plc, SignalConfig signalConfig) {
        this.sensorId = sensorId;
        this.name = name;
        this.plc = plc;
        this.signalConfig = signalConfig;
        this.isActive = true;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getSensorId() {
        return sensorId;
    }

    public void setSensorId(String sensorId) {
        this.sensorId = sensorId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Boolean getIsActive() {
        return isActive;
    }

    public void setIsActive(Boolean isActive) {
        this.isActive = isActive;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    public PLC getPlc() {
        return plc;
    }

    public void setPlc(PLC plc) {
        this.plc = plc;
    }

    public SignalConfig getSignalConfig() {
        return signalConfig;
    }

    public void setSignalConfig(SignalConfig signalConfig) {
        this.signalConfig = signalConfig;
    }

    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}