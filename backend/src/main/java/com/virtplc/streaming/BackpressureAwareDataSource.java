package com.virtplc.streaming;

import com.virtplc.grpc.GrpcDtos.SensorData;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

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
public class BackpressureAwareDataSource {

    private final DataPipelineProcessor dataPipeline;
    private final Random random = new Random();
    private final AtomicLong sequenceGenerator = new AtomicLong(1);

    private static final List<String> SENSOR_IDS = List.of(
            "temperature_1", "pressure_1", "flow_rate_1", "voltage_1", "current_1",
            "temperature_2", "pressure_2", "flow_rate_2", "voltage_2", "current_2");

    /**
     * Generate simulated sensor data stream with backpressure handling
     */
    public Flux<SensorData> generateSensorDataStream(int dataRatePerSecond) {
        return Flux.interval(java.time.Duration.ofMillis(1000 / dataRatePerSecond))
                .onBackpressureDrop(dropped -> log.warn("Data generation backpressure: dropped tick {}", dropped))
                .flatMap(tick -> generateSensorDataBatch())
                .transform(dataPipeline::processDataStream) // Apply pipeline processing with backpressure
                .doOnNext(data -> log.debug("Generated sensor data: {} = {}", data.getSensorId(), data.getValue()))
                .doOnError(error -> log.error("Error in data generation stream", error));
    }

    /**
     * Generate a batch of sensor data
     */
    private Mono<SensorData> generateSensorDataBatch() {
        return Mono.fromCallable(() -> {
            String sensorId = SENSOR_IDS.get(random.nextInt(SENSOR_IDS.size()));
            double value = generateRealisticValue(sensorId);
            long timestamp = Instant.now().toEpochMilli();

            return SensorData.builder()
                    .sensorId(sensorId)
                    .value(value)
                    .timestamp(timestamp)
                    .metadata(java.util.Map.of("source", "simulated", "quality", "good"))
                    .build();
        });
    }

    /**
     * Generate realistic sensor values based on sensor type
     */
    private double generateRealisticValue(String sensorId) {
        if (sensorId.startsWith("temperature")) {
            // Temperature: 20-80°C with some noise
            return 20 + random.nextDouble() * 60 + (random.nextDouble() - 0.5) * 5;
        } else if (sensorId.startsWith("pressure")) {
            // Pressure: 0-10 bar with noise
            return random.nextDouble() * 10 + (random.nextDouble() - 0.5) * 0.5;
        } else if (sensorId.startsWith("flow_rate")) {
            // Flow rate: 0-100 L/min with noise
            return random.nextDouble() * 100 + (random.nextDouble() - 0.5) * 10;
        } else if (sensorId.startsWith("voltage")) {
            // Voltage: 220-250V with noise
            return 220 + random.nextDouble() * 30 + (random.nextDouble() - 0.5) * 5;
        } else if (sensorId.startsWith("current")) {
            // Current: 0-20A with noise
            return random.nextDouble() * 20 + (random.nextDouble() - 0.5) * 2;
        } else {
            return random.nextDouble() * 100;
        }
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
                        double value = generateRealisticValue(sensorId);

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
                SENSOR_IDS.size(),
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