package com.virtplc.service;

import lombok.extern.slf4j.Slf4j;
import org.eclipse.milo.opcua.sdk.client.OpcUaClient;
import org.eclipse.milo.opcua.stack.core.types.builtin.DataValue;
import org.eclipse.milo.opcua.stack.core.types.builtin.NodeId;
import org.eclipse.milo.opcua.stack.core.types.builtin.StatusCode;
import org.eclipse.milo.opcua.stack.core.types.builtin.Variant;
import org.eclipse.milo.opcua.stack.core.types.enumerated.TimestampsToReturn;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.util.concurrent.CompletableFuture;

/**
 * OPC UA Client service for connecting to PLC simulator.
 */
@Service
@Slf4j
@ConditionalOnProperty(name = "opcua.client.enabled", havingValue = "true", matchIfMissing = true)
public class OpcUaClientService {

    @Value("${opcua.client.endpoint:opc.tcp://plc-simulator:4840}")
    private String endpointUrl;

    @Value("${opcua.client.request-timeout:5000}")
    private Integer requestTimeout;

    @Value("${opcua.client.session-timeout:60000}")
    private Integer sessionTimeout;

    private OpcUaClient client;
    private boolean connected = false;

    @PostConstruct
    public void initialize() {
        log.info("Initializing OPC UA Client for endpoint: {}", endpointUrl);
        try {
            connect();
        } catch (Exception e) {
            log.error("Failed to initialize OPC UA client: {}", e.getMessage());
        }
    }

    @PreDestroy
    public void shutdown() {
        disconnect();
    }

    /**
     * Connect to OPC UA server
     */
    public void connect() throws Exception {
        if (connected) {
            log.warn("OPC UA client already connected");
            return;
        }

        log.info("Connecting to OPC UA server at: {}", endpointUrl);

        client = OpcUaClient.create(endpointUrl);
        client.connect().get();
        connected = true;
        log.info("Successfully connected to OPC UA server");
    }

    /**
     * Disconnect from OPC UA server
     */
    public void disconnect() {
        if (client != null && connected) {
            try {
                client.disconnect().get();
                connected = false;
                log.info("Disconnected from OPC UA server");
            } catch (Exception e) {
                log.error("Error disconnecting from OPC UA server: {}", e.getMessage());
            }
        }
    }

    /**
     * Read a value from OPC UA node
     */
    public Object readValue(String nodeId) {
        return readValue(NodeId.parse(nodeId));
    }

    /**
     * Read a value from OPC UA node
     */
    public Object readValue(NodeId nodeId) {
        if (!connected || client == null) {
            log.warn("OPC UA client not connected, cannot read value");
            return null;
        }

        try {
            CompletableFuture<DataValue> future = client.readValue(0.0, TimestampsToReturn.Both, nodeId);
            DataValue dataValue = future.get();

            if (dataValue.getStatusCode().equals(StatusCode.GOOD)) {
                Variant variant = dataValue.getValue();
                if (variant != null) {
                    return variant.getValue();
                }
            } else {
                log.warn("OPC UA read failed for node {}: {}", nodeId, dataValue.getStatusCode());
            }
        } catch (Exception e) {
            log.error("Error reading OPC UA value for node {}: {}", nodeId, e.getMessage());
        }

        return null;
    }

    /**
     * Write a value to OPC UA node
     */
    public boolean writeValue(String nodeId, Object value) {
        return writeValue(NodeId.parse(nodeId), value);
    }

    /**
     * Write a value to OPC UA node
     */
    public boolean writeValue(NodeId nodeId, Object value) {
        if (!connected || client == null) {
            log.warn("OPC UA client not connected, cannot write value");
            return false;
        }

        try {
            DataValue dataValue = DataValue.valueOnly(new Variant(value));
            CompletableFuture<StatusCode> future = client.writeValue(nodeId, dataValue);
            StatusCode statusCode = future.get();

            if (statusCode.equals(StatusCode.GOOD)) {
                log.debug("Successfully wrote value {} to node {}", value, nodeId);
                return true;
            } else {
                log.warn("OPC UA write failed for node {}: {}", nodeId, statusCode);
                return false;
            }
        } catch (Exception e) {
            log.error("Error writing OPC UA value for node {}: {}", nodeId, e.getMessage());
            return false;
        }
    }

    /**
     * Check if client is connected
     */
    public boolean isConnected() {
        return connected;
    }

    /**
     * Reconnect if disconnected
     */
    public void reconnect() {
        if (!connected) {
            try {
                connect();
            } catch (Exception e) {
                log.error("Failed to reconnect to OPC UA server: {}", e.getMessage());
            }
        }
    }
}