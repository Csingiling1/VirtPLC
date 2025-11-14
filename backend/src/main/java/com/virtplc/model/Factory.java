package com.virtplc.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "factories")
public class Factory {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String factoryId;

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
    @JoinColumn(name = "manufacturer_id", nullable = false)
    private Manufacturer manufacturer;

    @OneToMany(mappedBy = "factory", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<PLC> plcs;

    // Factory layout properties
    @Column
    private String shape = "rectangle";

    @Column
    private Integer width = 100;

    @Column
    private Integer height = 80;

    @Column
    private Double widthMeters = 50.0;

    @Column
    private Double heightMeters = 40.0;

    @Column
    private String wireframeColor = "#3b82f6";

    // Constructors
    public Factory() {
    }

    public Factory(String factoryId, String name, String description, Manufacturer manufacturer) {
        this.factoryId = factoryId;
        this.name = name;
        this.description = description;
        this.manufacturer = manufacturer;
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

    public String getFactoryId() {
        return factoryId;
    }

    public void setFactoryId(String factoryId) {
        this.factoryId = factoryId;
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

    public Manufacturer getManufacturer() {
        return manufacturer;
    }

    public void setManufacturer(Manufacturer manufacturer) {
        this.manufacturer = manufacturer;
    }

    public List<PLC> getPlcs() {
        return plcs;
    }

    public void setPlcs(List<PLC> plcs) {
        this.plcs = plcs;
    }

    public String getShape() {
        return shape;
    }

    public void setShape(String shape) {
        this.shape = shape;
    }

    public Integer getWidth() {
        return width;
    }

    public void setWidth(Integer width) {
        this.width = width;
    }

    public Integer getHeight() {
        return height;
    }

    public void setHeight(Integer height) {
        this.height = height;
    }

    public Double getWidthMeters() {
        return widthMeters;
    }

    public void setWidthMeters(Double widthMeters) {
        this.widthMeters = widthMeters;
    }

    public Double getHeightMeters() {
        return heightMeters;
    }

    public void setHeightMeters(Double heightMeters) {
        this.heightMeters = heightMeters;
    }

    public String getWireframeColor() {
        return wireframeColor;
    }

    public void setWireframeColor(String wireframeColor) {
        this.wireframeColor = wireframeColor;
    }

    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}