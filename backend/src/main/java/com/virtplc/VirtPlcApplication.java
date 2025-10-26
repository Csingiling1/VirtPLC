package com.virtplc;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * VirtPLC Backend Application
 *
 * Spring Boot application providing:
 * - OPC-UA server for factory equipment communication
 * - REST API for frontend and external clients
 * - TimescaleDB integration for historical data
 * - JWT-based authentication
 * - Scheduled data collection from OPC UA
 */
@SpringBootApplication
@EnableScheduling
public class VirtPlcApplication {

    public static void main(String[] args) {
        SpringApplication.run(VirtPlcApplication.class, args);
    }
}
