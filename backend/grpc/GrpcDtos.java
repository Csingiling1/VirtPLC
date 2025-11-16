package com.virtplc.grpc;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.HashMap;
import java.util.Map;

/**
 * Data Transfer Objects for gRPC services
 */
public class GrpcDtos {

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SensorData {
        private String sensorId;
        private String deviceId;
        private double value;
        private long timestamp;
        @Builder.Default
        private Map<String, String> metadata = new HashMap<>();
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SensorDataBatch {
        private java.util.List<SensorData> data;
        private long batchId;
        private long batchTimestamp;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SensorDataQuery {
        private String sensorId;
        private long startTime;
        private long endTime;
        private int limit;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AIProcessingResult {
        private String sensorId;
        private double predictedValue;
        private double confidence;
        private String anomalyType;
        @Builder.Default
        private Map<String, Double> features = new HashMap<>();
        private long processingTimestamp;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AIPredictionRequest {
        private java.util.List<String> sensorIds;
        private String modelType;
        private int predictionHorizon;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AIPrediction {
        private String sensorId;
        private java.util.List<Double> predictions;
        private java.util.List<Long> timestamps;
        private double confidence;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SimulationData {
        private String sensorId;
        private double value;
        private long timestamp;
        private String simulationScenario;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DashboardUpdate {
        private String dashboardId;
        private java.util.List<SensorData> sensorData;
        private java.util.List<AIProcessingResult> aiResults;
        private long timestamp;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DashboardSubscription {
        private java.util.List<String> sensorIds;
        private String dashboardId;
        private int updateInterval;
    }
}