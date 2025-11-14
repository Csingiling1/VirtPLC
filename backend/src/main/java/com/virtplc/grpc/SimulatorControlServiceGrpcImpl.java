package com.virtplc.grpc;

import com.virtplc.grpc.GrpcDtos.*;
import com.virtplc.grpc.GrpcServices.SimulatorControlService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

/**
 * Simulator Control Service implementation
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class SimulatorControlServiceGrpcImpl implements SimulatorControlService {

    private final WebClient simulatorWebClient;

    @Override
    public Mono<Void> startSimulation() {
        log.info("Starting simulation");

        return simulatorWebClient.post()
                .uri("/api/simulator/start")
                .retrieve()
                .bodyToMono(Void.class)
                .doOnSuccess(v -> log.info("Simulation started successfully"))
                .doOnError(error -> log.error("Error starting simulation", error));
    }

    @Override
    public Mono<Void> stopSimulation() {
        log.info("Stopping simulation");

        return simulatorWebClient.post()
                .uri("/api/simulator/stop")
                .retrieve()
                .bodyToMono(Void.class)
                .doOnSuccess(v -> log.info("Simulation stopped successfully"))
                .doOnError(error -> log.error("Error stopping simulation", error));
    }

    @Override
    public Flux<SimulationData> streamSimulationData() {
        log.info("Starting simulation data stream");

        return simulatorWebClient.get()
                .uri("/api/simulator/stream")
                .retrieve()
                .bodyToFlux(SimulationData.class)
                .doOnNext(data -> log.debug("Received simulation data: {} = {}", data.getSensorId(), data.getValue()))
                .doOnError(error -> log.error("Error in simulation data stream", error))
                .doOnCancel(() -> log.info("Simulation data stream cancelled"))
                .doOnComplete(() -> log.info("Simulation data stream completed"));
    }
}