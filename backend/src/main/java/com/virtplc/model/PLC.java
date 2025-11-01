package com.virtplc.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "plcs")
public class PLC {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String plcId;

    @Column(nullable = false)
    private String name;

    @Column
    private String description;

    @Column(nullable = false)
    private Boolean isActive = true;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "factory_id", nullable = false)
    private Factory factory;

    @OneToMany(mappedBy = "plc", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Sensor> sensors;

    // Position within factory (in meters from top-left corner)
    @Column
    private Double xPosition = 0.0;

    @Column
    private Double yPosition = 0.0;

    // Physical dimensions (in meters)
    @Column
    private Double width = 2.0;

    @Column
    private Double height = 1.5;

    // Constructors
    public PLC() {
    }

    public PLC(String plcId, String name, String description, Factory factory) {
        this.plcId = plcId;
        this.name = name;
        this.description = description;
        this.factory = factory;
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

    public String getPlcId() {
        return plcId;
    }

    public void setPlcId(String plcId) {
        this.plcId = plcId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
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

    public Factory getFactory() {
        return factory;
    }

    public void setFactory(Factory factory) {
        this.factory = factory;
    }

    public List<Sensor> getSensors() {
        return sensors;
    }

    public void setSensors(List<Sensor> sensors) {
        this.sensors = sensors;
    }

    public Double getXPosition() {
        return xPosition;
    }

    public void setXPosition(Double xPosition) {
        this.xPosition = xPosition;
    }

    public Double getYPosition() {
        return yPosition;
    }

    public void setYPosition(Double yPosition) {
        this.yPosition = yPosition;
    }

    public Double getWidth() {
        return width;
    }

    public void setWidth(Double width) {
        this.width = width;
    }

    public Double getHeight() {
        return height;
    }

    public void setHeight(Double height) {
        this.height = height;
    }

    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}