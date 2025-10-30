package com.virtplc.websocket;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

/**
 * WebSocket configuration for real-time data streaming
 */
@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {

    private final SensorDataWebSocketHandler sensorDataWebSocketHandler;
    private final DashboardWebSocketHandler dashboardWebSocketHandler;

    public WebSocketConfig(SensorDataWebSocketHandler sensorDataWebSocketHandler,
            DashboardWebSocketHandler dashboardWebSocketHandler) {
        this.sensorDataWebSocketHandler = sensorDataWebSocketHandler;
        this.dashboardWebSocketHandler = dashboardWebSocketHandler;
    }

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        // Sensor data streaming endpoint with compression
        registry.addHandler(sensorDataWebSocketHandler, "/ws/sensor-data")
                .setAllowedOrigins("*")
                .withSockJS(); // Fallback for browsers that don't support WebSocket

        // Dashboard updates endpoint
        registry.addHandler(dashboardWebSocketHandler, "/ws/dashboard")
                .setAllowedOrigins("*")
                .withSockJS();
    }
}