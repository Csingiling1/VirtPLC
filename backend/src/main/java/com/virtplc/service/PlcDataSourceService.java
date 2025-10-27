package com.virtplc.service;

import com.virtplc.opcua.NodeManager;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * Data source service for real PLC via OPC-UA.
 * Used in production when connecting to actual PLC hardware.
 */
@Slf4j
@Service
@RequiredArgsConstructor
@ConditionalOnProperty(name = "data.source", havingValue = "plc", matchIfMissing = false)
public class PlcDataSourceService implements DataSourceService {

    private final Optional<NodeManager> nodeManager;

    @Value("${plc.name:Production PLC}")
    private String plcName;

    @Override
    public Map<String, Object> getLatestSensorData() {
        log.debug("Fetching data from real PLC via OPC-UA");
        
        Map<String, Object> data = new HashMap<>();
        
        if (!nodeManager.isPresent()) {
            log.error("NodeManager not available for PLC data source");
            data.put("systemStatus", "Error - OPC-UA Not Available");
            data.put("dataSource", "PLC");
            return data;
        }
        
        try {
            NodeManager nm = nodeManager.get();
            // Read from OPC-UA nodes (real PLC)
            data.put("motor1Speed", nm.getMotor1Speed());
            data.put("motor1Temp", nm.getMotor1Temp());
            data.put("motor1Run", true);  // Assume running if we can read data
            data.put("motor1Fault", false);
            
            data.put("motor2Speed", nm.getMotor2Speed());
            data.put("motor2Temp", nm.getMotor2Temp());
            data.put("motor2Run", true);
            data.put("motor2Fault", false);
            
            data.put("conveyor1Speed", nm.getConveyor1Speed());
            data.put("conveyor1Run", true);
            
            data.put("sensor1Value", nm.getSensor1Value());
            data.put("sensor2Value", nm.getSensor2Value());
            
            data.put("systemStatus", "Running");
            data.put("dataSource", "PLC");
            
            log.debug("Successfully fetched data from PLC: {} fields", data.size());
            
        } catch (Exception e) {
            log.error("Failed to fetch data from PLC: {}", e.getMessage());
            // Return default values on error
            data.put("systemStatus", "Error");
            data.put("dataSource", "PLC");
        }
        
        return data;
    }

    @Override
    public boolean isAvailable() {
        if (!nodeManager.isPresent()) {
            return false;
        }
        
        try {
            // Try to read a simple value to check connectivity
            nodeManager.get().getMotor1Speed();
            return true;
        } catch (Exception e) {
            log.debug("PLC not available: {}", e.getMessage());
            return false;
        }
    }

    @Override
    public String getDataSourceName() {
        return plcName;
    }
}
