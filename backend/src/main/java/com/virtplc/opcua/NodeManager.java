package com.virtplc.opcua;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import java.util.Random;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * Manages OPC-UA nodes for the virtual factory.
 * Creates and updates Motor, Conveyor, Sensor, and System nodes.
 * 
 * TODO: Implement full OPC-UA node management when Eclipse Milo is properly configured.
 * This is a stub for initial project setup.
 */
@Slf4j
@Component
@ConditionalOnProperty(name = "opcua.server.enabled", havingValue = "true", matchIfMissing = true)
public class NodeManager {

    private final Random random = new Random();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);

    @Value("${opcua.server.namespace:http://virtplc.accenture.com/factory}")
    private String namespace;

    // Simulated values for demonstration
    private volatile double motor1Speed = 0.0;
    private volatile double motor1Temp = 25.0;
    private volatile double motor2Speed = 0.0;
    private volatile double motor2Temp = 25.0;
    private volatile double conveyor1Speed = 0.0;
    private volatile double sensor1Value = 0.0;
    private volatile boolean sensor2Value = false;

    @PostConstruct
    public void initialize() {
        log.info("Initializing NodeManager with namespace: {}", namespace);
        log.info("TODO: Create OPC-UA address space with folders and variables");
        log.info("- Motor1: Speed, Temperature, Run, Fault");
        log.info("- Motor2: Speed, Temperature, Run, Fault");
        log.info("- Conveyor1: Speed, Run");
        log.info("- Sensors: Sensor1_Value, Sensor2_Value");
        log.info("- System: Status, Timestamp");
        
        // Start simulation for demo purposes
        startSimulation();
    }

    private void startSimulation() {
        scheduler.scheduleAtFixedRate(() -> {
            try {
                // Simulate motor speeds (50-100 RPM)
                motor1Speed = 50 + random.nextDouble() * 50;
                motor2Speed = 50 + random.nextDouble() * 50;
                
                // Simulate temperatures (25-85°C)
                motor1Temp = 25 + random.nextDouble() * 60;
                motor2Temp = 25 + random.nextDouble() * 60;
                
                // Simulate conveyor speed (10-50 cm/s)
                conveyor1Speed = 10 + random.nextDouble() * 40;
                
                // Simulate sensor values
                sensor1Value = random.nextDouble() * 100;
                sensor2Value = random.nextBoolean();
                
                log.debug("Simulated values - M1 Speed: {}, M1 Temp: {}, Sensor1: {}", 
                         motor1Speed, motor1Temp, sensor1Value);
                
            } catch (Exception e) {
                log.error("Error updating simulated values", e);
            }
        }, 1, 2, TimeUnit.SECONDS);
    }

    // Getter methods for simulated values (to be used by REST API)
    public double getMotor1Speed() { return motor1Speed; }
    public double getMotor1Temp() { return motor1Temp; }
    public double getMotor2Speed() { return motor2Speed; }
    public double getMotor2Temp() { return motor2Temp; }
    public double getConveyor1Speed() { return conveyor1Speed; }
    public double getSensor1Value() { return sensor1Value; }
    public boolean getSensor2Value() { return sensor2Value; }
}
