package com.virtplc.config;

import lombok.extern.slf4j.Slf4j;
import org.eclipse.milo.opcua.sdk.server.OpcUaServer;
import org.eclipse.milo.opcua.sdk.server.api.config.OpcUaServerConfig;
import org.eclipse.milo.opcua.stack.core.types.builtin.LocalizedText;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;

/**
 * Configuration for OPC-UA Server using Eclipse Milo.
 */
@Slf4j
@Configuration
@ConditionalOnProperty(name = "opcua.server.enabled", havingValue = "true", matchIfMissing = true)
public class OPCUAServerConfig {

    @Value("${opcua.server.port:4840}")
    private int opcuaPort;

    @Value("${opcua.server.endpoint:opc.tcp://0.0.0.0:4840}")
    private String opcuaEndpoint;

    @Value("${opcua.server.namespace:http://virtplc.accenture.com/factory}")
    private String namespace;

    private OpcUaServer server;

    @Bean
    public OpcUaServer opcUaServer() throws Exception {
        // Create server configuration
        OpcUaServerConfig serverConfig = OpcUaServerConfig.builder()
                .setApplicationName(LocalizedText.english("VirtPLC OPC-UA Server"))
                .setApplicationUri("urn:virtplc:opcua:server")
                .setProductUri("urn:virtplc:product")
                .build();

        // Create the server
        server = new OpcUaServer(serverConfig);

        log.info("OPC-UA Server created with endpoint: {}", opcuaEndpoint);
        return server;
    }

    @PostConstruct
    public void initialize() throws Exception {
        log.info("OPC-UA Server configuration initialized");
        log.info("Port: {}, Endpoint: {}, Namespace: {}", opcuaPort, opcuaEndpoint, namespace);

        // Start the server
        if (server != null) {
            server.startup().get();
            log.info("OPC-UA Server started successfully on port {}", opcuaPort);
        }
    }

    @PreDestroy
    public void shutdown() {
        if (server != null) {
            try {
                server.shutdown().get();
                log.info("OPC-UA Server shut down successfully");
            } catch (Exception e) {
                log.error("Error shutting down OPC-UA Server", e);
            }
        }
    }
}
