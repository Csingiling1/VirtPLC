package com.virtplc.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Data model for sensor readings from the factory.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SensorData {
    private Long timestamp;
    private Double motor1Speed;
    private Double motor1Temp;
    private Boolean motor1Run;
    private Boolean motor1Fault;
    private Double motor2Speed;
    private Double motor2Temp;
    private Boolean motor2Run;
    private Boolean motor2Fault;
    private Double conveyor1Speed;
    private Boolean conveyor1Run;
    private Double sensor1Value;
    private Boolean sensor2Value;
    private String systemStatus;
}
