package com.virtplc.grpc;

import com.virtplc.grpc.plcstream.PlcReading;
import com.virtplc.grpc.plcstream.PlcStreamServiceGrpc;
import com.virtplc.grpc.plcstream.StreamAck;
import io.grpc.stub.StreamObserver;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.devh.boot.grpc.server.service.GrpcService;
import org.springframework.stereotype.Service;

import java.util.concurrent.atomic.AtomicLong;

@GrpcService
@Service
@Slf4j
@RequiredArgsConstructor
public class PlcStreamServiceGrpcImpl extends PlcStreamServiceGrpc.PlcStreamServiceImplBase {

    private final AtomicLong processedReadings = new AtomicLong(0);

    @Override
    public StreamObserver<PlcReading> streamReadings(StreamObserver<StreamAck> responseObserver) {
        log.info("New collector connected for streaming readings");

        return new StreamObserver<PlcReading>() {
            private long batchCount = 0;

            @Override
            public void onNext(PlcReading reading) {
                try {
                    // Process the reading
                    log.debug("Received reading: tenant={}, manufacturer={}, factory={}, plc={}, sensor={}, value={}",
                            reading.getTenantId(), reading.getManufacturerId(), reading.getFactoryId(),
                            reading.getPlcId(), reading.getSensorId(), reading.getValue());

                    // TODO: Store in database via repository
                    // For now, just count the readings
                    long totalProcessed = processedReadings.incrementAndGet();
                    batchCount++;

                    // Send acknowledgment every 100 readings
                    if (batchCount % 100 == 0) {
                        StreamAck ack = StreamAck.newBuilder()
                                .setSuccess(true)
                                .setMessage("Processed " + batchCount + " readings")
                                .setProcessedCount(totalProcessed)
                                .build();

                        responseObserver.onNext(ack);
                        log.info("Sent batch acknowledgment: {} readings processed", batchCount);
                    }

                } catch (Exception e) {
                    log.error("Error processing reading: {}", e.getMessage(), e);
                    // Send error acknowledgment
                    StreamAck errorAck = StreamAck.newBuilder()
                            .setSuccess(false)
                            .setMessage("Error processing reading: " + e.getMessage())
                            .setProcessedCount(processedReadings.get())
                            .build();
                    responseObserver.onNext(errorAck);
                }
            }

            @Override
            public void onError(Throwable t) {
                log.error("Stream error from collector: {}", t.getMessage(), t);
            }

            @Override
            public void onCompleted() {
                log.info("Collector stream completed. Total readings processed in session: {}", batchCount);

                // Send final acknowledgment
                StreamAck finalAck = StreamAck.newBuilder()
                        .setSuccess(true)
                        .setMessage("Stream completed successfully")
                        .setProcessedCount(processedReadings.get())
                        .build();

                responseObserver.onNext(finalAck);
                responseObserver.onCompleted();
            }
        };
    }
}