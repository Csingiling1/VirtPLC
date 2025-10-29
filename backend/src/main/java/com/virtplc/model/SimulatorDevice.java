package com.virtplc.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

/**
 * Enhanced device model for simulator integration
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SimulatorDevice {
    private String id;
    private String name;
    private String description;
    private String deviceType;
    private List<SignalConfig> signals;
    @JsonProperty("is_active")
    private Boolean isActive;
    @JsonProperty("created_at")
    private Long createdAt;
    @JsonProperty("updated_at")
    private Long updatedAt;
}