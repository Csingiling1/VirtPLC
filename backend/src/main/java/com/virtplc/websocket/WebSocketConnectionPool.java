package com.virtplc.websocket;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * WebSocket connection pool manager for performance optimization
 */
@Slf4j
@Component
public class WebSocketConnectionPool {

    private final ConcurrentHashMap<String, ConnectionInfo> activeConnections = new ConcurrentHashMap<>();
    private final ScheduledExecutorService cleanupExecutor = Executors.newSingleThreadScheduledExecutor();
    private final AtomicInteger totalConnections = new AtomicInteger(0);
    private final AtomicInteger activeStreams = new AtomicInteger(0);

    public WebSocketConnectionPool() {
        // Schedule cleanup of stale connections every 5 minutes
        cleanupExecutor.scheduleAtFixedRate(this::cleanupStaleConnections, 5, 5, TimeUnit.MINUTES);
    }

    /**
     * Register a new WebSocket connection
     */
    public void registerConnection(String sessionId, String connectionType) {
        ConnectionInfo info = new ConnectionInfo(sessionId, connectionType, System.currentTimeMillis());
        activeConnections.put(sessionId, info);
        totalConnections.incrementAndGet();

        log.debug("Registered WebSocket connection: {} ({})", sessionId, connectionType);
    }

    /**
     * Unregister a WebSocket connection
     */
    public void unregisterConnection(String sessionId) {
        ConnectionInfo removed = activeConnections.remove(sessionId);
        if (removed != null) {
            totalConnections.decrementAndGet();
            log.debug("Unregistered WebSocket connection: {} ({})", sessionId, removed.connectionType);
        }
    }

    /**
     * Register an active data stream
     */
    public void registerStream(String sessionId) {
        activeStreams.incrementAndGet();
        log.debug("Registered active stream for session: {}", sessionId);
    }

    /**
     * Unregister an active data stream
     */
    public void unregisterStream(String sessionId) {
        activeStreams.decrementAndGet();
        log.debug("Unregistered active stream for session: {}", sessionId);
    }

    /**
     * Get connection pool statistics
     */
    public ConnectionPoolStats getStats() {
        return new ConnectionPoolStats(
                totalConnections.get(),
                activeStreams.get(),
                activeConnections.size());
    }

    /**
     * Cleanup stale connections (connections that haven't sent a ping in 30
     * minutes)
     */
    private void cleanupStaleConnections() {
        long cutoffTime = System.currentTimeMillis() - (30 * 60 * 1000L); // 30 minutes ago
        int cleanedCount = 0;

        for (var entry : activeConnections.entrySet()) {
            if (entry.getValue().lastActivity < cutoffTime) {
                activeConnections.remove(entry.getKey());
                totalConnections.decrementAndGet();
                cleanedCount++;
            }
        }

        if (cleanedCount > 0) {
            log.info("Cleaned up {} stale WebSocket connections", cleanedCount);
        }
    }

    /**
     * Update last activity timestamp for a connection
     */
    public void updateActivity(String sessionId) {
        ConnectionInfo info = activeConnections.get(sessionId);
        if (info != null) {
            info.lastActivity = System.currentTimeMillis();
        }
    }

    /**
     * Shutdown the connection pool
     */
    public void shutdown() {
        cleanupExecutor.shutdown();
        try {
            if (!cleanupExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                cleanupExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            cleanupExecutor.shutdownNow();
            Thread.currentThread().interrupt();
        }

        activeConnections.clear();
        log.info("WebSocket connection pool shut down");
    }

    /**
     * Connection information
     */
    private static class ConnectionInfo {
        final String connectionType;
        volatile long lastActivity;

        ConnectionInfo(String sessionId, String connectionType, long lastActivity) {
            this.connectionType = connectionType;
            this.lastActivity = lastActivity;
        }
    }

    /**
     * Connection pool statistics
     */
    public static class ConnectionPoolStats {
        public final int totalConnections;
        public final int activeStreams;
        public final int uniqueSessions;

        public ConnectionPoolStats(int totalConnections, int activeStreams, int uniqueSessions) {
            this.totalConnections = totalConnections;
            this.activeStreams = activeStreams;
            this.uniqueSessions = uniqueSessions;
        }
    }
}