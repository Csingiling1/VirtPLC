package com.virtplc.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * JPA entity for sensor data stored in TimescaleDB.
 * Uses hypertable for time-series optimization.
 */
@Entity
@Table(name = "sensor_data")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SensorDataEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @CreationTimestamp
    @Column(name = "timestamp", nullable = false)
    private LocalDateTime timestamp;

    @Column(name = "motor1_speed")
    private Double motor1Speed;

    @Column(name = "motor1_temp")
    private Double motor1Temp;

    @Column(name = "motor1_run")
    private Boolean motor1Run;

    @Column(name = "motor1_fault")
    private Boolean motor1Fault;

    @Column(name = "motor2_speed")
    private Double motor2Speed;

    @Column(name = "motor2_temp")
    private Double motor2Temp;

    @Column(name = "motor2_run")
    private Boolean motor2Run;

    @Column(name = "motor2_fault")
    private Boolean motor2Fault;

    @Column(name = "conveyor1_speed")
    private Double conveyor1Speed;

    @Column(name = "conveyor1_run")
    private Boolean conveyor1Run;

    @Column(name = "sensor1_value")
    private Double sensor1Value;

    @Column(name = "sensor2_value")
    private Boolean sensor2Value;

    @Column(name = "system_status")
    private String systemStatus;

    @Column(name = "device_id")
    private String deviceId;

    @Column(name = "quality")
    private Integer quality;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "company_id", nullable = false)
    private Company company;
}