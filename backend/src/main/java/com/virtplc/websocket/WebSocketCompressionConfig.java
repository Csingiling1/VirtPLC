package com.virtplc.websocket;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.server.standard.ServletServerContainerFactoryBean;

/**
 * WebSocket compression and performance configuration
 */
@Configuration
public class WebSocketCompressionConfig {

    /**
     * Configure WebSocket container with performance optimizations
     */
    @Bean
    public ServletServerContainerFactoryBean createWebSocketContainer() {
        ServletServerContainerFactoryBean container = new ServletServerContainerFactoryBean();
        container.setMaxTextMessageBufferSize(8192);
        container.setMaxBinaryMessageBufferSize(8192);
        container.setMaxSessionIdleTimeout(30 * 60 * 1000L); // 30 minutes
        container.setAsyncSendTimeout(10 * 1000L); // 10 seconds

        return container;
    }
}