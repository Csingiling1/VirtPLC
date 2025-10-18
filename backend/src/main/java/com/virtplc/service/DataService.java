package com.virtplc.service;

import com.virtplc.model.SensorData;
import com.virtplc.opcua.NodeManager;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

/**
 * Service for retrieving and managing sensor data.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DataService {

    private final NodeManager nodeManager;

    /**
     * Get the latest sensor data from OPC-UA nodes.
     */
    public SensorData getLatestData() {
        log.debug("Fetching latest sensor data");
        
        return SensorData.builder()
                .timestamp(System.currentTimeMillis())
                .motor1Speed(nodeManager.getMotor1Speed())
                .motor1Temp(nodeManager.getMotor1Temp())
                .motor1Run(true)
                .motor1Fault(false)
                .motor2Speed(nodeManager.getMotor2Speed())
                .motor2Temp(nodeManager.getMotor2Temp())
                .motor2Run(true)
                .motor2Fault(false)
                .conveyor1Speed(nodeManager.getConveyor1Speed())
                .conveyor1Run(true)
                .sensor1Value(nodeManager.getSensor1Value())
                .sensor2Value(nodeManager.getSensor2Value())
                .systemStatus("Running")
                .build();
    }

    /**
     * Get historical data for a time range.
     * TODO: Implement TimeBase DB query for historical data.
     */
    public List<SensorData> getDataRange(Long startTime, Long endTime) {
        log.debug("Fetching data range: {} to {}", startTime, endTime);
        
        // TODO: Query TimeBase DB for historical data
        // For now, return sample data
        List<SensorData> result = new ArrayList<>();
        
        // Generate some sample historical data
        long interval = (endTime - startTime) / 10;
        for (int i = 0; i < 10; i++) {
            result.add(SensorData.builder()
                    .timestamp(startTime + (i * interval))
                    .motor1Speed(50 + Math.random() * 50)
                    .motor1Temp(25 + Math.random() * 60)
                    .motor1Run(true)
                    .motor1Fault(false)
                    .motor2Speed(50 + Math.random() * 50)
                    .motor2Temp(25 + Math.random() * 60)
                    .motor2Run(true)
                    .motor2Fault(false)
                    .conveyor1Speed(10 + Math.random() * 40)
                    .conveyor1Run(true)
                    .sensor1Value(Math.random() * 100)
                    .sensor2Value(Math.random() > 0.5)
                    .systemStatus("Running")
                    .build());
        }
        
        return result;
    }
}
