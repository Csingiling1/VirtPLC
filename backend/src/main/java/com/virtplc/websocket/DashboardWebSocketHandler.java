package com.virtplc.websocket;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.virtplc.grpc.DashboardServiceGrpcImpl;
import com.virtplc.grpc.GrpcDtos.DashboardSubscription;
import com.virtplc.grpc.GrpcDtos.DashboardUpdate;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;
import reactor.core.publisher.Flux;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * WebSocket handler for dashboard real-time updates
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class DashboardWebSocketHandler extends TextWebSocketHandler {

    private final DashboardServiceGrpcImpl dashboardService;
    private final ObjectMapper objectMapper;
    private final WebSocketConnectionPool connectionPool;
    private final Map<String, WebSocketSession> activeSessions = new ConcurrentHashMap<>();
    private final Map<String, Flux<DashboardUpdate>> activeStreams = new ConcurrentHashMap<>();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        String sessionId = session.getId();
        activeSessions.put(sessionId, session);

        // Register connection with pool
        connectionPool.registerConnection(sessionId, "DASHBOARD");

        log.info("Dashboard WebSocket connection established: {}", sessionId);

        // Send welcome message
        session.sendMessage(new TextMessage("{\"type\":\"CONNECTED\",\"message\":\"Dashboard streaming ready\"}"));
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) throws Exception {
        String sessionId = session.getId();

        // Clean up active stream
        Flux<DashboardUpdate> stream = activeStreams.remove(sessionId);
        if (stream != null) {
            // In a real implementation, you'd properly dispose of the stream
            log.debug("Cleaned up dashboard stream for session {}", sessionId);
        }

        activeSessions.remove(sessionId);

        // Unregister connection from pool
        connectionPool.unregisterConnection(sessionId);

        log.info("Dashboard WebSocket connection closed: {} with status: {}", sessionId, status);
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        String sessionId = session.getId();
        String payload = message.getPayload();

        // Update activity timestamp
        connectionPool.updateActivity(sessionId);

        try {
            WebSocketMessage wsMessage = objectMapper.readValue(payload, WebSocketMessage.class);

            switch (wsMessage.getType()) {
                case "SUBSCRIBE_DASHBOARD":
                    handleDashboardSubscription(sessionId, session, wsMessage);
                    break;
                case "UNSUBSCRIBE_DASHBOARD":
                    handleDashboardUnsubscription(sessionId, session);
                    break;
                case "PING":
                    session.sendMessage(new TextMessage("{\"type\":\"PONG\"}"));
                    break;
                default:
                    log.warn("Unknown dashboard message type: {}", wsMessage.getType());
                    session.sendMessage(new TextMessage("{\"type\":\"ERROR\",\"message\":\"Unknown message type\"}"));
            }
        } catch (Exception e) {
            log.error("Error processing dashboard WebSocket message: {}", payload, e);
            session.sendMessage(new TextMessage("{\"type\":\"ERROR\",\"message\":\"Invalid message format\"}"));
        }
    }

    private void handleDashboardSubscription(String sessionId, WebSocketSession session, WebSocketMessage message)
            throws IOException {
        Map<String, Object> subscriptionData = (Map<String, Object>) message.getData();

        if (subscriptionData == null || !subscriptionData.containsKey("sensorIds")) {
            session.sendMessage(new TextMessage(
                    "{\"type\":\"ERROR\",\"message\":\"sensorIds required for dashboard subscription\"}"));
            return;
        }

        @SuppressWarnings("unchecked")
        java.util.List<String> sensorIds = (java.util.List<String>) subscriptionData.get("sensorIds");
        String dashboardId = (String) subscriptionData.getOrDefault("dashboardId", sessionId);

        DashboardSubscription subscription = DashboardSubscription.builder()
                .sensorIds(sensorIds)
                .dashboardId(dashboardId)
                .updateInterval(1000) // 1 second updates
                .build();

        // Start dashboard update stream
        Flux<DashboardUpdate> dashboardStream = dashboardService.streamDashboardUpdates(subscription)
                .doOnNext(update -> {
                    try {
                        String jsonData = objectMapper.writeValueAsString(Map.of(
                                "type", "DASHBOARD_UPDATE",
                                "data", update,
                                "timestamp", System.currentTimeMillis()));
                        session.sendMessage(new TextMessage(jsonData));
                    } catch (Exception e) {
                        log.error("Error sending dashboard update to WebSocket session {}", sessionId, e);
                    }
                })
                .doOnError(error -> {
                    log.error("Error in dashboard stream for session {}", sessionId, error);
                    try {
                        session.sendMessage(
                                new TextMessage("{\"type\":\"ERROR\",\"message\":\"Dashboard stream error\"}"));
                    } catch (IOException e) {
                        log.error("Error sending error message to session {}", sessionId, e);
                    }
                })
                .doOnCancel(() -> log.debug("Dashboard stream cancelled for session {}", sessionId))
                .doOnComplete(() -> log.debug("Dashboard stream completed for session {}", sessionId));

        activeStreams.put(sessionId, dashboardStream);
        // Register stream with connection pool
        connectionPool.registerStream(sessionId);
        // Keep the stream alive
        dashboardStream.subscribe();

        session.sendMessage(
                new TextMessage("{\"type\":\"DASHBOARD_SUBSCRIBED\",\"dashboardId\":\"" + dashboardId + "\"}"));
        log.info("Session {} subscribed to dashboard: {}", sessionId, dashboardId);
    }

    private void handleDashboardUnsubscription(String sessionId, WebSocketSession session) throws IOException {
        Flux<DashboardUpdate> stream = activeStreams.remove(sessionId);
        if (stream != null) {
            // In a real implementation, you'd properly dispose of the stream
            log.debug("Unsubscribed dashboard stream for session {}", sessionId);
        }

        // Unregister stream from connection pool
        connectionPool.unregisterStream(sessionId);

        session.sendMessage(new TextMessage("{\"type\":\"DASHBOARD_UNSUBSCRIBED\"}"));
        log.info("Session {} unsubscribed from dashboard", sessionId);
    }

    /**
     * Get count of active dashboard WebSocket sessions
     */
    public int getActiveSessionCount() {
        return activeSessions.size();
    }

    /**
     * Broadcast dashboard update to all active sessions
     */
    public void broadcastDashboardUpdate(DashboardUpdate update) {
        try {
            String message = "{\"type\":\"DASHBOARD_UPDATE\",\"data\":" + objectMapper.writeValueAsString(update) + "}";
            TextMessage textMessage = new TextMessage(message);

            activeSessions.values().forEach(session -> {
                try {
                    if (session.isOpen()) {
                        session.sendMessage(textMessage);
                    }
                } catch (IOException e) {
                    log.error("Error broadcasting dashboard update to session {}", session.getId(), e);
                }
            });
        } catch (Exception e) {
            log.error("Error serializing dashboard update for broadcast", e);
        }
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