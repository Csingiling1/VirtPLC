package com.virtplc.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.persistence.*;
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
@Embeddable
public class SignalConfig {
    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private String unit;

    @Column
    private Double value;

    @Column
    private String generator;

    @Column
    @JsonProperty("is_running")
    private Boolean isRunning;

    // Generator parameters
    @Column
    @JsonProperty("min_value")
    private Double minValue;

    @Column
    @JsonProperty("max_value")
    private Double maxValue;

    @Column
    private Double mean;

    @Column
    @JsonProperty("std_dev")
    private Double stdDev;

    @Column
    private Double rate;

    @Column
    private Double frequency;

    @Column
    private Double amplitude;

    @Column(name = "\"signal_offset\"")
    private Double offset;

    @Column
    @JsonProperty("step_size")
    private Double stepSize;

    // Runtime state
    @Column
    @JsonProperty("last_update")
    private Double lastUpdate;
}