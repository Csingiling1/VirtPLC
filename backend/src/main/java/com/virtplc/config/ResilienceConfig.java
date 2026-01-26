package com.virtplc.config;

import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import io.github.resilience4j.retry.Retry;
import io.github.resilience4j.retry.RetryConfig;
import io.github.resilience4j.retry.RetryRegistry;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;

/**
 * Resilience4j configuration for circuit breakers and retry mechanisms
 * to improve microservice reliability and fault tolerance
 */
@Configuration
public class ResilienceConfig {

    @Bean
    public CircuitBreakerRegistry circuitBreakerRegistry() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
                .failureRateThreshold(50) // Open circuit if 50% of calls fail
                .waitDurationInOpenState(Duration.ofMillis(10000)) // Wait 10s before trying again
                .permittedNumberOfCallsInHalfOpenState(3) // Allow 3 calls in half-open state
                .slidingWindowSize(10) // Consider last 10 calls
                .build();

        return CircuitBreakerRegistry.of(config);
    }

    @Bean
    public CircuitBreaker aiServiceCircuitBreaker(CircuitBreakerRegistry registry) {
        return registry.circuitBreaker("ai-service");
    }

    @Bean
    public CircuitBreaker simulatorCircuitBreaker(CircuitBreakerRegistry registry) {
        return registry.circuitBreaker("simulator");
    }

    @Bean
    public RetryRegistry retryRegistry() {
        RetryConfig config = RetryConfig.custom()
                .maxAttempts(3)
                .waitDuration(Duration.ofMillis(500))
                .retryExceptions(Exception.class)
                .build();

        return RetryRegistry.of(config);
    }

    @Bean
    public Retry aiServiceRetry(RetryRegistry registry) {
        return registry.retry("ai-service-retry");
    }
}