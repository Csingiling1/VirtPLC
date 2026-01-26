package com.virtplc.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import io.swagger.v3.oas.models.servers.Server;
import io.swagger.v3.oas.models.Components;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

/**
 * OpenAPI/Swagger configuration for API documentation
 */
@Configuration
public class OpenApiConfig {

        @Bean
        public OpenAPI virtPlcOpenAPI() {
                return new OpenAPI()
                                .info(new Info()
                                                .title("VirtPLC Backend API")
                                                .description(
                                                                "Industrial IoT Platform API for factory automation, real-time monitoring, and AI-powered analytics. "
                                                                                +
                                                                                "This API provides comprehensive endpoints for device management, data ingestion, user authentication, "
                                                                                +
                                                                                "and dashboard functionality in a microservice architecture.")
                                                .version("1.0.0")
                                                .contact(new Contact()
                                                                .name("VirtPLC Development Team")
                                                                .email("dev@virtplc.com")
                                                                .url("https://github.com/Csingiling1/VirtPLC"))
                                                .license(new License()
                                                                .name("MIT License")
                                                                .url("https://opensource.org/licenses/MIT")))
                                .servers(List.of(
                                                new Server().url("http://localhost:18080")
                                                                .description("Local Development Server"),
                                                new Server().url("https://api.virtplc.com")
                                                                .description("Production Server"),
                                                new Server().url("http://localhost:8080")
                                                                .description("Direct Backend Access (Development)")))
                                .components(new Components()
                                                .addSecuritySchemes("bearerAuth",
                                                                new SecurityScheme()
                                                                                .type(SecurityScheme.Type.HTTP)
                                                                                .scheme("bearer")
                                                                                .bearerFormat("JWT")
                                                                                .description("JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""))
                                                .addSecuritySchemes("oauth2",
                                                                new SecurityScheme()
                                                                                .type(SecurityScheme.Type.OAUTH2)
                                                                                .description("OAuth2 authentication with Google and other providers")))
                                .security(List.of(
                                                new SecurityRequirement().addList("bearerAuth")));
        }
}