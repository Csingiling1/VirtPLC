package com.virtplc.pipeline;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

/**
 * Simplified data pipeline for MQTT-based data processing
 */
@Slf4j
@Service
public class DataPipelineService {

    /**
     * Process incoming MQTT data (placeholder for future real-time processing)
     */
    public Mono<Void> processMqttData(String topic, String payload) {
        return Mono.<Void>fromRunnable(() -> {
            log.debug("Processing MQTT data from topic: {}, payload length: {}", topic, payload.length());
            // Data is stored by the collector, so we just log for now
            // Future: Could implement real-time processing, alerting, etc.
        });
    }
}