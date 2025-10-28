package com.virtplc.config;

import com.virtplc.service.UserService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

/**
 * Initialize default data on application startup
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {

    private final UserService userService;

    @Override
    public void run(String... args) throws Exception {
        log.info("Initializing default data...");

        try {
            userService.createDefaultAdminUser();
            log.info("Default data initialization completed");
        } catch (Exception e) {
            log.error("Error initializing default data", e);
        }
    }
}