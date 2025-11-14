package com.virtplc.grpc;

import com.virtplc.grpc.GrpcDtos.*;
import com.virtplc.grpc.GrpcServices.AIService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.Instant;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * AI Service implementation for real-time AI processing
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AIServiceGrpcImpl implements AIService {

    private final WebClient aiServiceWebClient;
    private final Map<String, Flux<AIPrediction>> activePredictions = new ConcurrentHashMap<>();

    @Override
    public Mono<AIProcessingResult> processSensorData(SensorData sensorData) {
        log.info("Processing sensor data through AI service: {}", sensorData.getSensorId());

        return aiServiceWebClient.post()
                .uri("/api/ai/process")
                .bodyValue(sensorData)
                .retrieve()
                .bodyToMono(AIProcessingResult.class)
                .doOnNext(result -> log.debug("AI processing result: {}", result.getPredictedValue()))
                .doOnError(error -> log.error("Error processing sensor data through AI", error));
    }

    @Override
    public Flux<AIPrediction> streamAIPredictions(AIPredictionRequest request) {
        log.info("Starting AI prediction stream for sensors: {}", request.getSensorIds());

        String streamKey = String.join(",", request.getSensorIds()) + "_" + Instant.now().toEpochMilli();

        Flux<AIPrediction> predictionStream = aiServiceWebClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path("/api/ai/predictions/stream")
                        .queryParam("sensorIds", String.join(",", request.getSensorIds()))
                        .queryParam("model", request.getModelType())
                        .build())
                .retrieve()
                .bodyToFlux(AIPrediction.class)
                .doOnNext(prediction -> log.debug("Received AI prediction: {}", prediction.getPredictions()))
                .doOnError(error -> log.error("Error in AI prediction stream", error))
                .doOnCancel(() -> {
                    log.info("AI prediction stream cancelled for sensors: {}", request.getSensorIds());
                    activePredictions.remove(streamKey);
                })
                .doOnComplete(() -> {
                    log.info("AI prediction stream completed for sensors: {}", request.getSensorIds());
                    activePredictions.remove(streamKey);
                });

        activePredictions.put(streamKey, predictionStream);
        return predictionStream;
    }

    /**
     * Get active prediction streams count
     */
    public int getActivePredictionStreamsCount() {
        return activePredictions.size();
    }

    /**
     * Stop all active prediction streams
     */
    public void stopAllPredictionStreams() {
        activePredictions.clear();
        log.info("Stopped all active AI prediction streams");
    }
}