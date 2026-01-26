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
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.web.OAuth2AuthorizedClientRepository;
import org.springframework.security.oauth2.client.web.OAuth2AuthorizedClientRepository;
import org.springframework.security.oauth2.client.web.HttpSessionOAuth2AuthorizedClientRepository;
import org.springframework.beans.factory.annotation.Autowired;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@RequiredArgsConstructor
public class SecurityConfig {

        private final JwtAuthenticationFilter jwtAuthenticationFilter;
        private final CorsConfigurationSource corsConfigurationSource;

        @Autowired(required = false)
        private ClientRegistrationRepository clientRegistrationRepository;

        @Bean
        public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
                http
                                .cors(cors -> cors.configurationSource(corsConfigurationSource))
                                // CSRF disabled for stateless API (JWT-based auth)
                                // For production, consider enabling CSRF for state-changing operations
                                .csrf(AbstractHttpConfigurer::disable)
                                .headers(headers -> headers
                                                .frameOptions(frame -> frame.sameOrigin())
                                                .contentTypeOptions(content -> content.disable())
                                                .httpStrictTransportSecurity(hsts -> hsts
                                                                .includeSubDomains(true)
                                                                .maxAgeInSeconds(31536000)))
                                .authorizeHttpRequests(authz -> authz
                                                // Public endpoints
                                                .requestMatchers(HttpMethod.OPTIONS).permitAll()
                                                .requestMatchers("/swagger-ui.html").permitAll()
                                                .requestMatchers("/swagger-ui/**").permitAll()
                                                .requestMatchers("/api-docs/**").permitAll()
                                                .requestMatchers("/v3/api-docs/**").permitAll()
                                                .requestMatchers("/api/auth/**").permitAll()
                                                .requestMatchers("/oauth2/**").permitAll()
                                                .requestMatchers("/login/oauth2/**").permitAll()
                                                .requestMatchers("/actuator/**").permitAll()
                                                .requestMatchers("/health").permitAll()
                                                .requestMatchers("/api/data/health").permitAll()
                                                .requestMatchers(HttpMethod.OPTIONS, "/api/data/latest").permitAll()
                                                .requestMatchers("/api/data/latest").permitAll()
                                                .requestMatchers("/api/data/range").permitAll()
                                                .requestMatchers("/api/data/hierarchical").permitAll()
                                                .requestMatchers("/api/data/hierarchical-live").permitAll()
                                                .requestMatchers("/api/data/device/*/history").permitAll()
                                                .requestMatchers("/api/data/plc-data/latest").permitAll()
                                                .requestMatchers("/api/admin/device-assignments").permitAll()
                                                .requestMatchers(HttpMethod.GET, "/api/admin/factories").permitAll()
                                                .requestMatchers(HttpMethod.GET, "/api/admin/devices").permitAll()
                                                .requestMatchers(HttpMethod.POST, "/api/admin/factories").permitAll()
                                                .requestMatchers(HttpMethod.PUT, "/api/admin/factories/**").permitAll()
                                                .requestMatchers(HttpMethod.DELETE, "/api/admin/factories/**")
                                                .permitAll()
                                                .requestMatchers(HttpMethod.POST, "/api/data/ingest").permitAll()
                                                .requestMatchers("/api/simulator/**").permitAll() // Simulator endpoints
                                                                                                  // for dashboard
                                                .requestMatchers("/api/mcp/**").permitAll() // MCP endpoints for AI
                                                                                            // service
                                                .requestMatchers("/error").permitAll()
                                                // .requestMatchers("/api/dashboards/**").permitAll() // Dashboard
                                                // endpoints -
                                                // now require authentication

                                                // Protected endpoints
                                                .anyRequest().authenticated())
                                .sessionManagement(sess -> sess.sessionCreationPolicy(SessionCreationPolicy.STATELESS));

                // Only configure OAuth2 login if client registrations are available
                if (clientRegistrationRepository != null) {
                        http.oauth2Login(oauth2 -> oauth2
                                        .loginPage("/login")
                                        .successHandler((request, response, authentication) -> {
                                                // Handle successful OAuth2 login - redirect to frontend with
                                                // success indicator
                                                response.sendRedirect(
                                                                "http://localhost:5173/login?oauth2_success=true");
                                        })
                                        .failureHandler((request, response, exception) -> {
                                                // Handle OAuth2 login failure
                                                response.sendRedirect(
                                                                "http://localhost:5173/login?error=oauth2");
                                        }));
                }

                http.addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

                return http.build();
        }
}