package com.virtplc.model;

import com.fasterxml.jackson.annotation.JsonProperty;
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
    @JsonProperty("is_running")
    private Boolean isRunning;

    // Generator parameters
    @JsonProperty("min_value")
    private Double minValue;
    @JsonProperty("max_value")
    private Double maxValue;
    private Double mean;
    @JsonProperty("std_dev")
    private Double stdDev;
    private Double rate;
    private Double frequency;
    private Double amplitude;
    private Double offset;
    @JsonProperty("step_size")
    private Double stepSize;

    // Runtime state
    @JsonProperty("last_update")
    private Double lastUpdate;
}