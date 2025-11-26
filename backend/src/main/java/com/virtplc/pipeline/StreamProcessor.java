package com.virtplc.pipeline;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

/**
 * Simplified stream processor for MQTT-based data processing
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class StreamProcessor {

    private final DataPipelineService dataPipeline;

    /**
     * Process incoming MQTT data
     */
    public Mono<Void> processMqttData(String topic, String payload) {
        return dataPipeline.processMqttData(topic, payload)
                .doOnSuccess(v -> log.debug("Processed MQTT data from topic: {}", topic))
                .doOnError(error -> log.error("Error processing MQTT data", error));
    }
}