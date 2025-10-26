package com.virtplc.opcua;

import com.virtplc.service.OpcUaClientService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * Manages OPC-UA nodes for the virtual factory.
 * Reads data from PLC simulator via OPC UA client.
 */
@Slf4j
@Component
@RequiredArgsConstructor
@ConditionalOnProperty(name = "opcua.server.enabled", havingValue = "true", matchIfMissing = true)
public class NodeManager {

    private final OpcUaClientService opcUaClient;
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);

    @Value("${opcua.server.namespace:http://virtplc.accenture.com/factory}")
    private String namespace;

    // Cached values from OPC UA
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
        log.info("Reading data from PLC simulator via OPC UA");

        // Start periodic reading from OPC UA server
        startOpcUaReading();
    }

    private void startOpcUaReading() {
        scheduler.scheduleAtFixedRate(() -> {
            try {
                // Read values from PLC simulator via OPC UA
                updateValuesFromOpcUa();
                log.debug("Updated values from OPC UA - M1 Speed: {}, M1 Temp: {}, Sensor1: {}",
                         motor1Speed, motor1Temp, sensor1Value);

            } catch (Exception e) {
                log.error("Error reading from OPC UA server", e);
                // Try to reconnect if connection lost
                opcUaClient.reconnect();
            }
        }, 1, 2, TimeUnit.SECONDS);
    }

    private void updateValuesFromOpcUa() {
        // Read motor values
        Object motor1SpeedVal = opcUaClient.readValue("ns=2;s=Motor1.Speed");
        if (motor1SpeedVal instanceof Number) {
            motor1Speed = ((Number) motor1SpeedVal).doubleValue();
        }

        Object motor1TempVal = opcUaClient.readValue("ns=2;s=Motor1.Temperature");
        if (motor1TempVal instanceof Number) {
            motor1Temp = ((Number) motor1TempVal).doubleValue();
        }

        Object motor2SpeedVal = opcUaClient.readValue("ns=2;s=Motor2.Speed");
        if (motor2SpeedVal instanceof Number) {
            motor2Speed = ((Number) motor2SpeedVal).doubleValue();
        }

        Object motor2TempVal = opcUaClient.readValue("ns=2;s=Motor2.Temperature");
        if (motor2TempVal instanceof Number) {
            motor2Temp = ((Number) motor2TempVal).doubleValue();
        }

        // Read conveyor values
        Object conveyor1SpeedVal = opcUaClient.readValue("ns=2;s=Conveyor1.Speed");
        if (conveyor1SpeedVal instanceof Number) {
            conveyor1Speed = ((Number) conveyor1SpeedVal).doubleValue();
        }

        // Read sensor values
        Object sensor1Val = opcUaClient.readValue("ns=2;s=Sensor1.Value");
        if (sensor1Val instanceof Number) {
            sensor1Value = ((Number) sensor1Val).doubleValue();
        }

        Object sensor2Val = opcUaClient.readValue("ns=2;s=Sensor2.Value");
        if (sensor2Val instanceof Boolean) {
            sensor2Value = (Boolean) sensor2Val;
        }
    }

    // Getter methods for values read from OPC UA
    public double getMotor1Speed() { return motor1Speed; }
    public double getMotor1Temp() { return motor1Temp; }
    public double getMotor2Speed() { return motor2Speed; }
    public double getMotor2Temp() { return motor2Temp; }
    public double getConveyor1Speed() { return conveyor1Speed; }
    public double getSensor1Value() { return sensor1Value; }
    public boolean getSensor2Value() { return sensor2Value; }
}
