package com.virtplc.model;

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
    private Boolean isActive;
    private Long createdAt;
    private Long updatedAt;
}