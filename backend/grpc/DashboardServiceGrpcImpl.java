package com.virtplc.grpc;

import com.virtplc.grpc.GrpcDtos.*;
import com.virtplc.grpc.GrpcServices.DashboardService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Dashboard Service implementation for real-time dashboard updates
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DashboardServiceGrpcImpl implements DashboardService {

    private final SensorDataServiceGrpcImpl sensorDataService;
    private final AIServiceGrpcImpl aiService;
    private final SimulatorControlServiceGrpcImpl simulatorService;
    private final Map<String, Flux<DashboardUpdate>> activeSubscriptions = new ConcurrentHashMap<>();

    @Override
    public Flux<DashboardUpdate> streamDashboardUpdates(DashboardSubscription subscription) {
        log.info("Starting dashboard update stream for dashboard: {}", subscription.getDashboardId());

        String subscriptionKey = subscription.getDashboardId() + "_" + Instant.now().toEpochMilli();

        // Combine multiple data streams into dashboard updates
        Flux<DashboardUpdate> sensorDataStream = sensorDataService.streamSensorData()
                .filter(sensorData -> subscription.getSensorIds().contains(sensorData.getSensorId()))
                .bufferTimeout(10, java.time.Duration.ofMillis(100)) // Batch updates
                .map(sensorDataBatch -> {
                    DashboardUpdate update = new DashboardUpdate();
                    update.setDashboardId(subscription.getDashboardId());
                    update.setSensorData(sensorDataBatch);
                    update.setTimestamp(Instant.now().toEpochMilli());
                    return update;
                });

        Flux<DashboardUpdate> aiPredictionStream = aiService.streamAIPredictions(
                AIPredictionRequest.builder()
                        .sensorIds(subscription.getSensorIds())
                        .modelType("default")
                        .predictionHorizon(10)
                        .build())
                .map(aiPrediction -> {
                    DashboardUpdate update = new DashboardUpdate();
                    update.setDashboardId(subscription.getDashboardId());
                    update.setAiResults(List.of()); // Could be populated based on AI results
                    update.setTimestamp(Instant.now().toEpochMilli());
                    return update;
                });

        Flux<DashboardUpdate> simulationStream = simulatorService.streamSimulationData()
                .filter(simData -> subscription.getSensorIds().contains(simData.getSensorId()))
                .map(simData -> {
                    DashboardUpdate update = new DashboardUpdate();
                    update.setDashboardId(subscription.getDashboardId());
                    update.setSensorData(List.of()); // Could map simulation data to sensor data format
                    update.setTimestamp(Instant.now().toEpochMilli());
                    return update;
                });

        Flux<DashboardUpdate> dashboardStream = Flux.merge(sensorDataStream, aiPredictionStream, simulationStream)
                .doOnNext(update -> log.debug("Sending dashboard update for: {}", update.getDashboardId()))
                .doOnError(error -> log.error("Error in dashboard update stream", error))
                .doOnCancel(() -> {
                    log.info("Dashboard update stream cancelled for dashboard: {}", subscription.getDashboardId());
                    activeSubscriptions.remove(subscriptionKey);
                })
                .doOnComplete(() -> {
                    log.info("Dashboard update stream completed for dashboard: {}", subscription.getDashboardId());
                    activeSubscriptions.remove(subscriptionKey);
                });

        activeSubscriptions.put(subscriptionKey, dashboardStream);
        return dashboardStream;
    }

    /**
     * Get active dashboard subscriptions count
     */
    public int getActiveSubscriptionsCount() {
        return activeSubscriptions.size();
    }

    /**
     * Stop all active dashboard subscriptions
     */
    public void stopAllSubscriptions() {
        activeSubscriptions.clear();
        log.info("Stopped all active dashboard subscriptions");
    }
}