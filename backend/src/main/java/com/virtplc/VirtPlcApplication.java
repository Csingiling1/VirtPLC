package com.virtplc;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * VirtPLC Backend Application
 * 
 * Spring Boot application providing:
 * - OPC-UA server for factory equipment communication
 * - REST API for frontend and external clients
 * - TimeBaseDB integration for historical data
 * - JWT-based authentication
 */
@SpringBootApplication
public class VirtPlcApplication {

    public static void main(String[] args) {
        SpringApplication.run(VirtPlcApplication.class, args);
    }
}
