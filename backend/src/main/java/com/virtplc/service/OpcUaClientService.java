package com.virtplc.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * Stub service - OPC-UA functionality removed in favor of MQTT.
 */
@Service
@Slf4j
public class OpcUaClientService {

    public OpcUaClientService() {
        log.info("OPC-UA client service initialized (stub - MQTT used instead)");
    }

    // Stub methods - not implemented
    public Object readValue(String nodeId) {
        log.warn("OPC-UA readValue called but OPC-UA is disabled - using MQTT instead");
        return null;
    }
}