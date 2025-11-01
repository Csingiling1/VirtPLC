package com.virtplc.streaming;

import com.virtplc.grpc.GrpcDtos.SensorData;
import com.virtplc.service.OpcUaClientService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Flux;

import java.time.Instant;
import java.util.List;
import java.util.Random;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Backpressure-aware data source for sensor data
 */
@Slf4j
@Component
@RequiredArgsConstructor
@ConditionalOnProperty(name = "opcua.client.enabled", havingValue = "true")
public class BackpressureAwareDataSource {

    private final DataPipelineProcessor dataPipeline;
    private final OpcUaClientService opcUaClient;
    private final Random random = new Random();
    private final AtomicLong sequenceGenerator = new AtomicLong(1);

    // Node IDs can be configured via 'opcua.node.ids' (comma-separated). If not
    // provided,
    // we fall back to a sensible default used for testing.
    @Value("${opcua.node.ids:}")
    private String opcuaNodeIdsProperty;

    private List<String> nodeIds;

    @PostConstruct
    public void initNodeIds() {
        if (opcuaNodeIdsProperty != null && !opcuaNodeIdsProperty.isBlank()) {
            nodeIds = List.of(opcuaNodeIdsProperty.split("\\s*,\\s*"));
            log.info("Using configured OPC-UA node IDs: {}", nodeIds);
        } else {
            nodeIds = List.of(
                    "ns=2;s=demo-tenant.demo-mfg.demo-factory.PLC-001.temperature_0",
                    "ns=2;s=demo-tenant.demo-mfg.demo-factory.PLC-001.pressure_0",
                    "ns=2;s=demo-tenant.demo-mfg.demo-factory.PLC-001.flow_rate_0",
                    "ns=2;s=demo-tenant.demo-mfg.demo-factory.PLC-001.vibration_0",
                    "ns=2;s=demo-tenant.demo-mfg.demo-factory.PLC-002.temperature_1",
                    "ns=2;s=demo-tenant.demo-mfg.demo-factory.PLC-002.pressure_1",
                    "ns=2;s=demo-tenant.demo-mfg.demo-factory.PLC-002.flow_rate_1",
                    "ns=2;s=demo-tenant.demo-mfg.demo-factory.PLC-002.vibration_1");
            log.info("Using default OPC-UA node IDs: {}", nodeIds);
        }
    }

    /**
     * Generate simulated sensor data stream with backpressure handling
     */
    public Flux<SensorData> generateSensorDataStream(int dataRatePerSecond) {
        return opcUaClient.subscribeToSensorData(nodeIds)
                .sample(java.time.Duration.ofMillis(1000 / dataRatePerSecond))
                .onBackpressureDrop(dropped -> log.warn("Data generation backpressure: dropped data {}", dropped))
                .transform(dataPipeline::processDataStream) // Apply pipeline processing with backpressure
                .doOnNext(data -> log.debug("Generated sensor data: {} = {}", data.getSensorId(), data.getValue()))
                .doOnError(error -> log.error("Error in data generation stream", error));
    }

    /**
     * Connect to external data source (OPC-UA, MQTT, etc.) with backpressure
     */
    public Flux<SensorData> connectToExternalSource(String sourceUrl, List<String> sensorIds) {
        return Flux.<SensorData>create(sink -> {
            // In a real implementation, this would connect to OPC-UA server, MQTT broker,
            // etc.
            // For now, simulate connection with periodic data

            Flux<SensorData> simulatedExternalData = Flux.interval(java.time.Duration.ofMillis(500))
                    .map(tick -> {
                        String sensorId = sensorIds.get((int) (tick % sensorIds.size()));
                        double value = random.nextDouble() * 100;

                        return SensorData.builder()
                                .sensorId(sensorId)
                                .value(value)
                                .timestamp(Instant.now().toEpochMilli())
                                .metadata(java.util.Map.of("source", "external", "quality", "good"))
                                .build();
                    })
                    .doOnNext(sink::next)
                    .doOnError(sink::error)
                    .doOnCancel(() -> {
                        log.info("External data source connection cancelled");
                        sink.complete();
                    });

            // Apply backpressure-aware processing
            dataPipeline.processDataStream(simulatedExternalData)
                    .subscribe(
                            data -> sink.next(data),
                            error -> {
                                log.error("Error from external data source", error);
                                sink.error(error);
                            },
                            () -> sink.complete());
        })
                .onBackpressureBuffer(1000, data -> {
                    log.warn("External source backpressure: buffering data for {}", data.getSensorId());
                });
    }

    /**
     * Get data source statistics
     */
    public DataSourceStats getStats() {
        return new DataSourceStats(
                sequenceGenerator.get(),
                nodeIds.size(),
                dataPipeline.getStats());
    }

    /**
     * Data source statistics
     */
    public static class DataSourceStats {
        public final long totalGenerated;
        public final int activeSensors;
        public final DataPipelineProcessor.PipelineStats pipelineStats;

        public DataSourceStats(long totalGenerated, int activeSensors,
                DataPipelineProcessor.PipelineStats pipelineStats) {
            this.totalGenerated = totalGenerated;
            this.activeSensors = activeSensors;
            this.pipelineStats = pipelineStats;
        }
    }
}