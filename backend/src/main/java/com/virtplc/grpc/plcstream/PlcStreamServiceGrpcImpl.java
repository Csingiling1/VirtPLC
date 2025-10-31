package com.virtplc.grpc.plcstream;

import com.virtplc.model.TelemetryData;
import com.virtplc.service.TelemetryIngestionService;
import io.grpc.stub.StreamObserver;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.devh.boot.grpc.server.service.GrpcService;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.concurrent.atomic.AtomicLong;

/**
 * gRPC service implementation for streaming PLC telemetry data from collectors.
 * Handles bidirectional streaming between collectors and backend.
 */
@Slf4j
@GrpcService
@Service
@RequiredArgsConstructor
public class PlcStreamServiceGrpcImpl extends PlcStreamServiceGrpc.PlcStreamServiceImplBase {

    private final TelemetryIngestionService telemetryIngestionService;

    @Override
    public StreamObserver<PlcReading> streamReadings(StreamObserver<StreamAck> responseObserver) {
        return new StreamObserver<PlcReading>() {
            private final AtomicLong processedCount = new AtomicLong(0);

            @Override
            public void onNext(PlcReading reading) {
                try {
                    log.debug("Received telemetry reading: tenant={}, manufacturer={}, factory={}, plc={}, sensor={}",
                            reading.getTenantId(), reading.getManufacturerId(), reading.getFactoryId(),
                            reading.getPlcId(), reading.getSensorId());

                    // Convert gRPC message to domain entity
                    TelemetryData telemetryData = TelemetryData.builder()
                            .tenantId(reading.getTenantId())
                            .manufacturerId(reading.getManufacturerId())
                            .factoryId(reading.getFactoryId())
                            .plcId(reading.getPlcId())
                            .sensorId(reading.getSensorId())
                            .value(reading.getValue())
                            .unit(reading.getUnit())
                            .timestamp(Instant.ofEpochMilli(reading.getTimestamp().getSeconds() * 1000 +
                                    reading.getTimestamp().getNanos() / 1000000))
                            .metadata(reading.getMetadata())
                            .build();

                    // Process and store the telemetry data
                    telemetryIngestionService.ingestTelemetry(telemetryData);

                    // Update processed count
                    long count = processedCount.incrementAndGet();

                    // Send acknowledgment every 100 readings or for debugging
                    if (count % 100 == 0) {
                        StreamAck ack = StreamAck.newBuilder()
                                .setSuccess(true)
                                .setMessage("Processed " + count + " readings successfully")
                                .setProcessedCount(count)
                                .build();
                        responseObserver.onNext(ack);
                        log.info("Sent acknowledgment for {} readings from tenant {}",
                                count, reading.getTenantId());
                    }

                } catch (Exception e) {
                    log.error("Error processing telemetry reading: {}", e.getMessage(), e);

                    // Send error acknowledgment
                    StreamAck errorAck = StreamAck.newBuilder()
                            .setSuccess(false)
                            .setMessage("Error processing reading: " + e.getMessage())
                            .setProcessedCount(processedCount.get())
                            .build();
                    responseObserver.onNext(errorAck);
                }
            }

            @Override
            public void onError(Throwable t) {
                log.error("Stream error from collector: {}", t.getMessage(), t);
                // Could implement reconnection logic here
            }

            @Override
            public void onCompleted() {
                log.info("Stream completed from collector. Total processed: {}", processedCount.get());

                // Send final acknowledgment
                StreamAck finalAck = StreamAck.newBuilder()
                        .setSuccess(true)
                        .setMessage("Stream completed successfully")
                        .setProcessedCount(processedCount.get())
                        .build();
                responseObserver.onNext(finalAck);
                responseObserver.onCompleted();
            }
        };
    }
}