package com.virtplc.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Signal configuration for simulator devices
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SignalConfig {
    private String name;
    private String unit;
    private Double value;
    private String generator;
    private Boolean isRunning;

    // Generator parameters
    private Double minValue;
    private Double maxValue;
    private Double mean;
    private Double stdDev;
    private Double rate;
    private Double frequency;
    private Double amplitude;
    private Double offset;
    private Double stepSize;

    // Runtime state
    private Double lastUpdate;
}