package com.virtplc.websocket;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.virtplc.grpc.GrpcDtos.SensorData;
import com.virtplc.grpc.SensorDataServiceGrpcImpl;
import com.virtplc.metrics.VirtPlcMetricsService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;
import reactor.core.publisher.Flux;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * WebSocket handler for real-time sensor data streaming with compression
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class SensorDataWebSocketHandler extends TextWebSocketHandler {

    private final SensorDataServiceGrpcImpl sensorDataService;
    private final ObjectMapper objectMapper;
    private final WebSocketConnectionPool connectionPool;
    private final VirtPlcMetricsService metricsService;
    private final Map<String, WebSocketSession> activeSessions = new ConcurrentHashMap<>();
    private final Map<String, List<String>> sessionSubscriptions = new ConcurrentHashMap<>();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        String sessionId = session.getId();
        activeSessions.put(sessionId, session);
        sessionSubscriptions.put(sessionId, new CopyOnWriteArrayList<>());

        // Register connection with pool
        connectionPool.registerConnection(sessionId, "SENSOR_DATA");

        // Track metrics
        metricsService.incrementActiveWebSocketConnections();

        log.info("WebSocket connection established: {}", sessionId);

        // Send welcome message
        session.sendMessage(new TextMessage("{\"type\":\"CONNECTED\",\"message\":\"Sensor data streaming ready\"}"));
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) throws Exception {
        String sessionId = session.getId();
        activeSessions.remove(sessionId);
        sessionSubscriptions.remove(sessionId);

        // Unregister connection from pool
        connectionPool.unregisterConnection(sessionId);

        // Track metrics
        metricsService.decrementActiveWebSocketConnections();

        log.info("WebSocket connection closed: {} with status: {}", sessionId, status);
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        String sessionId = session.getId();
        String payload = message.getPayload();

        // Update activity timestamp
        connectionPool.updateActivity(sessionId);

        // Track metrics
        metricsService.incrementWebSocketMessagesReceived();

        try {
            WebSocketMessage wsMessage = objectMapper.readValue(payload, WebSocketMessage.class);

            switch (wsMessage.getType()) {
                case "SUBSCRIBE":
                    handleSubscribe(sessionId, session, wsMessage);
                    break;
                case "UNSUBSCRIBE":
                    handleUnsubscribe(sessionId, session, wsMessage);
                    break;
                case "PING":
                    session.sendMessage(new TextMessage("{\"type\":\"PONG\"}"));
                    break;
                default:
                    log.warn("Unknown message type: {}", wsMessage.getType());
                    session.sendMessage(new TextMessage("{\"type\":\"ERROR\",\"message\":\"Unknown message type\"}"));
            }
        } catch (Exception e) {
            log.error("Error processing WebSocket message: {}", payload, e);
            session.sendMessage(new TextMessage("{\"type\":\"ERROR\",\"message\":\"Invalid message format\"}"));
        }
    }

    private void handleSubscribe(String sessionId, WebSocketSession session, WebSocketMessage message)
            throws IOException {
        @SuppressWarnings("unchecked")
        List<String> sensorIds = (List<String>) message.getData().get("sensorIds");

        if (sensorIds == null || sensorIds.isEmpty()) {
            session.sendMessage(
                    new TextMessage("{\"type\":\"ERROR\",\"message\":\"sensorIds required for subscription\"}"));
            return;
        }

        sessionSubscriptions.get(sessionId).addAll(sensorIds);

        // Start streaming sensor data for subscribed sensors
        Flux<SensorData> dataStream = sensorDataService.streamSensorData()
                .filter(data -> sensorIds.contains(data.getSensorId()))
                .doOnNext(sensorData -> {
                    try {
                        String jsonData = objectMapper.writeValueAsString(Map.of(
                                "type", "SENSOR_DATA",
                                "data", sensorData,
                                "timestamp", System.currentTimeMillis()));
                        session.sendMessage(new TextMessage(jsonData));
                    } catch (Exception e) {
                        log.error("Error sending sensor data to WebSocket session {}", sessionId, e);
                    }
                })
                .doOnError(error -> {
                    log.error("Error in sensor data stream for session {}", sessionId, error);
                    try {
                        session.sendMessage(new TextMessage("{\"type\":\"ERROR\",\"message\":\"Stream error\"}"));
                    } catch (IOException e) {
                        log.error("Error sending error message to session {}", sessionId, e);
                    }
                });

        // Register stream with connection pool
        connectionPool.registerStream(sessionId);

        // Keep the stream alive (in a real implementation, you'd manage subscriptions
        // properly)
        dataStream.subscribe();

        session.sendMessage(new TextMessage(
                "{\"type\":\"SUBSCRIBED\",\"sensorIds\":" + objectMapper.writeValueAsString(sensorIds) + "}"));
        log.info("Session {} subscribed to sensors: {}", sessionId, sensorIds);
    }

    private void handleUnsubscribe(String sessionId, WebSocketSession session, WebSocketMessage message)
            throws IOException {
        @SuppressWarnings("unchecked")
        List<String> sensorIds = (List<String>) message.getData().get("sensorIds");

        if (sensorIds != null) {
            sessionSubscriptions.get(sessionId).removeAll(sensorIds);
            // Unregister stream from connection pool
            connectionPool.unregisterStream(sessionId);
            session.sendMessage(new TextMessage(
                    "{\"type\":\"UNSUBSCRIBED\",\"sensorIds\":" + objectMapper.writeValueAsString(sensorIds) + "}"));
            log.info("Session {} unsubscribed from sensors: {}", sessionId, sensorIds);
        }
    }

    /**
     * Get count of active WebSocket sessions
     */
    public int getActiveSessionCount() {
        return activeSessions.size();
    }

    /**
     * Broadcast message to all active sessions
     */
    public void broadcast(String message) {
        TextMessage textMessage = new TextMessage(message);
        activeSessions.values().forEach(session -> {
            try {
                if (session.isOpen()) {
                    session.sendMessage(textMessage);
                }
            } catch (IOException e) {
                log.error("Error broadcasting to session {}", session.getId(), e);
            }
        });
    }

    /**
     * WebSocket message DTO
     */
    public static class WebSocketMessage {
        private String type;
        private Map<String, Object> data;

        public String getType() {
            return type;
        }

        public void setType(String type) {
            this.type = type;
        }

        public Map<String, Object> getData() {
            return data;
        }

        public void setData(Map<String, Object> data) {
            this.data = data;
        }
    }
}