package com.virtplc.security;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.http.HttpMethod;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    private final CorsConfigurationSource corsConfigurationSource;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .cors(cors -> cors.configurationSource(corsConfigurationSource))
                .csrf(AbstractHttpConfigurer::disable)
                .authorizeHttpRequests(authz -> authz
                        // Public endpoints
                        .requestMatchers(HttpMethod.OPTIONS).permitAll()
                        .requestMatchers("/api/auth/**").permitAll()
                        .requestMatchers("/actuator/**").permitAll()
                        .requestMatchers("/health").permitAll()
                        .requestMatchers("/api/data/health").permitAll()
                        .requestMatchers(HttpMethod.OPTIONS, "/api/data/latest").permitAll()
                        .requestMatchers("/api/data/latest").permitAll()
                        .requestMatchers("/api/data/range").permitAll()
                        .requestMatchers("/api/data/hierarchical").permitAll()
                        .requestMatchers("/api/admin/device-assignments").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/admin/factories").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/admin/devices").permitAll()
                        .requestMatchers(HttpMethod.POST, "/api/admin/factories").permitAll()
                        .requestMatchers(HttpMethod.PUT, "/api/admin/factories/**").permitAll()
                        .requestMatchers(HttpMethod.DELETE, "/api/admin/factories/**").permitAll()
                        .requestMatchers(HttpMethod.POST, "/api/data/ingest").permitAll()
                        .requestMatchers("/api/simulator/**").permitAll() // Simulator endpoints for dashboard
                        .requestMatchers("/api/mcp/**").permitAll() // MCP endpoints for AI service
                        .requestMatchers("/error").permitAll()
                        // .requestMatchers("/api/dashboards/**").permitAll() // Dashboard endpoints -
                        // now require authentication

                        // Protected endpoints
                        .anyRequest().authenticated())
                .sessionManagement(sess -> sess.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}