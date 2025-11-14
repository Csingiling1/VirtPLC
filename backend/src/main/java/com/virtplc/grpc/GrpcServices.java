package com.virtplc.grpc;

import com.virtplc.grpc.GrpcDtos.*;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

/**
 * gRPC Service Interfaces for real-time communication
 */
public interface GrpcServices {

    /**
     * Sensor Data Service - for real-time sensor streaming
     */
    interface SensorDataService {
        Flux<SensorData> streamSensorData();

        Mono<Void> uploadSensorDataBatch(SensorDataBatch batch);

        Flux<SensorData> getSensorDataHistory(SensorDataQuery query);
    }

    /**
     * AI Service - for real-time AI processing
     */
    interface AIService {
        Mono<AIProcessingResult> processSensorData(SensorData sensorData);

        Flux<AIPrediction> streamAIPredictions(AIPredictionRequest request);
    }

    /**
     * Simulator Control Service
     */
    interface SimulatorControlService {
        Mono<Void> startSimulation();

        Mono<Void> stopSimulation();

        Flux<SimulationData> streamSimulationData();
    }

    /**
     * Dashboard Service - for real-time dashboard updates
     */
    interface DashboardService {
        Flux<DashboardUpdate> streamDashboardUpdates(DashboardSubscription subscription);
    }
}