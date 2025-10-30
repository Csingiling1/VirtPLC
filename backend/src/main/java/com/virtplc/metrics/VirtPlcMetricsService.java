package com.virtplc.metrics;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Custom metrics service for VirtPLC application monitoring
 * Tracks business-specific metrics for sensor data, WebSocket connections,
 * gRPC calls, and system performance
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class VirtPlcMetricsService {

    private final MeterRegistry meterRegistry;

    // Sensor Data Metrics
    private Counter sensorDataProcessed;
    private Counter sensorDataStored;
    private Counter sensorDataErrors;

    // WebSocket Metrics
    private final AtomicInteger activeWebSocketConnections = new AtomicInteger(0);
    private Counter websocketMessagesSent;
    private Counter websocketMessagesReceived;
    private Counter websocketConnectionErrors;

    // gRPC Metrics
    private Counter grpcRequestsTotal;
    private Counter grpcRequestsSuccessful;
    private Counter grpcRequestsFailed;
    private Timer grpcRequestDuration;

    // Data Pipeline Metrics
    private final AtomicLong dataPipelineBackpressureEvents = new AtomicLong(0);
    private Counter dataPipelineProcessed;
    private Counter dataPipelineDropped;

    // AI Service Metrics
    private Counter aiPredictionsRequested;
    private Counter aiPredictionsCompleted;
    private Timer aiPredictionDuration;

    // Simulator Metrics
    private final AtomicInteger activeSimulatorDevices = new AtomicInteger(0);
    private Counter simulatorCommandsExecuted;

    // Business Logic Metrics
    private Counter alertsTriggered;
    private Counter userActionsPerformed;

    @PostConstruct
    public void init() {
        // Initialize counters and timers
        sensorDataProcessed = Counter.builder("virtplc.sensor.data.processed")
                .description("Total number of sensor data points processed")
                .register(meterRegistry);

        sensorDataStored = Counter.builder("virtplc.sensor.data.stored")
                .description("Total number of sensor data points stored in database")
                .register(meterRegistry);

        sensorDataErrors = Counter.builder("virtplc.sensor.data.errors")
                .description("Total number of sensor data processing errors")
                .register(meterRegistry);

        websocketMessagesSent = Counter.builder("virtplc.websocket.messages.sent")
                .description("Total number of WebSocket messages sent")
                .register(meterRegistry);

        websocketMessagesReceived = Counter.builder("virtplc.websocket.messages.received")
                .description("Total number of WebSocket messages received")
                .register(meterRegistry);

        websocketConnectionErrors = Counter.builder("virtplc.websocket.connection.errors")
                .description("Total number of WebSocket connection errors")
                .register(meterRegistry);

        grpcRequestsTotal = Counter.builder("virtplc.grpc.requests.total")
                .description("Total number of gRPC requests")
                .register(meterRegistry);

        grpcRequestsSuccessful = Counter.builder("virtplc.grpc.requests.successful")
                .description("Total number of successful gRPC requests")
                .register(meterRegistry);

        grpcRequestsFailed = Counter.builder("virtplc.grpc.requests.failed")
                .description("Total number of failed gRPC requests")
                .register(meterRegistry);

        grpcRequestDuration = Timer.builder("virtplc.grpc.request.duration")
                .description("Duration of gRPC requests")
                .register(meterRegistry);

        dataPipelineProcessed = Counter.builder("virtplc.pipeline.data.processed")
                .description("Total number of data points processed through pipeline")
                .register(meterRegistry);

        dataPipelineDropped = Counter.builder("virtplc.pipeline.data.dropped")
                .description("Total number of data points dropped due to backpressure")
                .register(meterRegistry);

        aiPredictionsRequested = Counter.builder("virtplc.ai.predictions.requested")
                .description("Total number of AI predictions requested")
                .register(meterRegistry);

        aiPredictionsCompleted = Counter.builder("virtplc.ai.predictions.completed")
                .description("Total number of AI predictions completed")
                .register(meterRegistry);

        aiPredictionDuration = Timer.builder("virtplc.ai.prediction.duration")
                .description("Duration of AI prediction operations")
                .register(meterRegistry);

        simulatorCommandsExecuted = Counter.builder("virtplc.simulator.commands.executed")
                .description("Total number of simulator commands executed")
                .register(meterRegistry);

        alertsTriggered = Counter.builder("virtplc.alerts.triggered")
                .description("Total number of alerts triggered")
                .register(meterRegistry);

        userActionsPerformed = Counter.builder("virtplc.user.actions.performed")
                .description("Total number of user actions performed")
                .register(meterRegistry);

        // Register gauges for atomic values
        Gauge.builder("virtplc.websocket.connections.active", activeWebSocketConnections, AtomicInteger::get)
                .description("Number of active WebSocket connections")
                .register(meterRegistry);

        Gauge.builder("virtplc.pipeline.backpressure.events", dataPipelineBackpressureEvents, AtomicLong::get)
                .description("Number of backpressure events in data pipeline")
                .register(meterRegistry);

        Gauge.builder("virtplc.simulator.devices.active", activeSimulatorDevices, AtomicInteger::get)
                .description("Number of active simulator devices")
                .register(meterRegistry);
    }

    // Sensor Data Methods
    public void incrementSensorDataProcessed() {
        sensorDataProcessed.increment();
    }

    public void incrementSensorDataStored() {
        sensorDataStored.increment();
    }

    public void incrementSensorDataErrors() {
        sensorDataErrors.increment();
    }

    // WebSocket Methods
    public void incrementActiveWebSocketConnections() {
        activeWebSocketConnections.incrementAndGet();
        log.debug("WebSocket connection established. Active connections: {}", activeWebSocketConnections.get());
    }

    public void decrementActiveWebSocketConnections() {
        int current = activeWebSocketConnections.decrementAndGet();
        if (current < 0) {
            activeWebSocketConnections.set(0);
        }
        log.debug("WebSocket connection closed. Active connections: {}", activeWebSocketConnections.get());
    }

    public void incrementWebSocketMessagesSent() {
        websocketMessagesSent.increment();
    }

    public void incrementWebSocketMessagesReceived() {
        websocketMessagesReceived.increment();
    }

    public void incrementWebSocketConnectionErrors() {
        websocketConnectionErrors.increment();
    }

    // gRPC Methods
    public void recordGrpcRequest(Timer.Sample sample, boolean success) {
        grpcRequestsTotal.increment();
        if (success) {
            grpcRequestsSuccessful.increment();
        } else {
            grpcRequestsFailed.increment();
        }
        sample.stop(grpcRequestDuration);
    }

    // Data Pipeline Methods
    public void incrementDataPipelineProcessed() {
        dataPipelineProcessed.increment();
    }

    public void incrementDataPipelineDropped() {
        dataPipelineDropped.increment();
        dataPipelineBackpressureEvents.incrementAndGet();
    }

    // AI Service Methods
    public void recordAiPrediction(Timer.Sample sample, boolean success) {
        aiPredictionsRequested.increment();
        if (success) {
            aiPredictionsCompleted.increment();
        }
        sample.stop(aiPredictionDuration);
    }

    // Simulator Methods
    public void incrementActiveSimulatorDevices() {
        activeSimulatorDevices.incrementAndGet();
    }

    public void decrementActiveSimulatorDevices() {
        int current = activeSimulatorDevices.decrementAndGet();
        if (current < 0) {
            activeSimulatorDevices.set(0);
        }
    }

    public void incrementSimulatorCommandsExecuted() {
        simulatorCommandsExecuted.increment();
    }

    // Business Logic Methods
    public void incrementAlertsTriggered() {
        alertsTriggered.increment();
    }

    public void incrementUserActionsPerformed() {
        userActionsPerformed.increment();
    }

    // Utility Methods
    public int getActiveWebSocketConnections() {
        return activeWebSocketConnections.get();
    }

    public long getDataPipelineBackpressureEvents() {
        return dataPipelineBackpressureEvents.get();
    }

    public int getActiveSimulatorDevices() {
        return activeSimulatorDevices.get();
    }
}