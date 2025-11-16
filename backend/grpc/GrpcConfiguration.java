package com.virtplc.grpc;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

/**
 * Configuration for gRPC services and WebClient beans
 */
@Configuration
public class GrpcConfiguration {

    @Value("${ai-service.url:http://localhost:8000}")
    private String aiServiceUrl;

    @Value("${simulator.url:http://localhost:5000}")
    private String simulatorUrl;

    /**
     * WebClient for AI service communication
     */
    @Bean
    public WebClient aiServiceWebClient() {
        return WebClient.builder()
                .baseUrl(aiServiceUrl)
                .build();
    }

    /**
     * WebClient for simulator service communication
     */
    @Bean
    public WebClient simulatorWebClient() {
        return WebClient.builder()
                .baseUrl(simulatorUrl)
                .build();
    }
}