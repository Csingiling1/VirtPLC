package com.virtplc.api;

import com.virtplc.model.User;
import com.virtplc.service.AuthService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.oauth2.client.authentication.OAuth2AuthenticationToken;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
@Tag(name = "Authentication", description = "User authentication and authorization endpoints")
public class AuthController {

    private final AuthService authService;

    @PostMapping("/register")
    @Operation(summary = "Register a new user", description = "Creates a new user account with the provided information and returns a JWT token", responses = {
            @ApiResponse(responseCode = "200", description = "User registered successfully", content = @Content(mediaType = "application/json", schema = @Schema(example = "{\"message\": \"User registered successfully\", \"token\": \"jwt-token\", \"user\": {...}}"))),
            @ApiResponse(responseCode = "400", description = "Registration failed", content = @Content(mediaType = "application/json", schema = @Schema(example = "{\"error\": \"Registration failed\", \"message\": \"Error details\"}")))
    })
    public ResponseEntity<Map<String, Object>> register(@RequestBody RegisterRequest request) {
        try {
            User user = authService.registerUser(
                    request.getEmail(),
                    request.getPassword(),
                    request.getFirstName(),
                    request.getLastName(),
                    request.getCompanyName(),
                    request.getCompanyDomain());

            String token = authService.generateToken(user);

            java.util.HashMap<String, Object> userMap = new java.util.HashMap<>();
            userMap.put("id", user.getId());
            userMap.put("email", user.getEmail());
            userMap.put("firstName", user.getFirstName());
            userMap.put("lastName", user.getLastName());
            userMap.put("role", user.getRole().name());
            userMap.put("company", user.getCompany() != null ? Map.of(
                    "id", user.getCompany().getId(),
                    "name", user.getCompany().getName(),
                    "domain", user.getCompany().getDomain()) : null);
            userMap.put("manufacturer", user.getManufacturer() != null ? Map.of(
                    "id", user.getManufacturer().getId(),
                    "name", user.getManufacturer().getName(),
                    "manufacturerId", user.getManufacturer().getManufacturerId()) : null);

            return ResponseEntity.ok(Map.of(
                    "message", "User registered successfully",
                    "token", token,
                    "user", userMap));
        } catch (Exception e) {
            log.error("Registration error: {}", e.getMessage(), e);
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "Registration failed",
                    "message", e.getMessage() != null ? e.getMessage() : "Unknown error"));
        }
    }

    @PostMapping("/login")
    @Operation(summary = "Authenticate user", description = "Authenticates a user with email and password, returns JWT token on success", responses = {
            @ApiResponse(responseCode = "200", description = "Login successful", content = @Content(mediaType = "application/json", schema = @Schema(example = "{\"message\": \"Login successful\", \"token\": \"jwt-token\", \"user\": {...}}"))),
            @ApiResponse(responseCode = "400", description = "Invalid credentials", content = @Content(mediaType = "application/json", schema = @Schema(example = "{\"error\": \"Invalid credentials\"}")))
    })
    public ResponseEntity<Map<String, Object>> login(@RequestBody LoginRequest request) {
        try {
            var userOpt = authService.authenticateUser(request.getEmail(), request.getPassword());

            if (userOpt.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of(
                        "error", "Invalid credentials"));
            }

            User user = userOpt.get();
            String token = authService.generateToken(user);

            java.util.HashMap<String, Object> userMap = new java.util.HashMap<>();
            userMap.put("id", user.getId());
            userMap.put("email", user.getEmail());
            userMap.put("firstName", user.getFirstName());
            userMap.put("lastName", user.getLastName());
            userMap.put("role", user.getRole().name());
            userMap.put("company", user.getCompany() != null ? Map.of(
                    "id", user.getCompany().getId(),
                    "name", user.getCompany().getName(),
                    "domain", user.getCompany().getDomain()) : null);
            userMap.put("manufacturer", user.getManufacturer() != null ? Map.of(
                    "id", user.getManufacturer().getId(),
                    "name", user.getManufacturer().getName(),
                    "manufacturerId", user.getManufacturer().getManufacturerId()) : null);

            return ResponseEntity.ok(Map.of(
                    "message", "Login successful",
                    "token", token,
                    "user", userMap));
        } catch (Exception e) {
            log.error("Login error: {}", e.getMessage(), e);
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "Login failed",
                    "message", e.getMessage() != null ? e.getMessage() : "Unknown error"));
        }
    }

    @PostMapping("/validate")
    @Operation(summary = "Validate JWT token", description = "Validates a JWT token and returns user information if valid", responses = {
            @ApiResponse(responseCode = "200", description = "Token is valid", content = @Content(mediaType = "application/json", schema = @Schema(example = "{\"valid\": true, \"user\": {...}}"))),
            @ApiResponse(responseCode = "400", description = "Invalid token or format", content = @Content(mediaType = "application/json", schema = @Schema(example = "{\"valid\": false, \"error\": \"Invalid token\"}")))
    })
    public ResponseEntity<Map<String, Object>> validateToken(@RequestHeader("Authorization") String authHeader) {
        try {
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                return ResponseEntity.badRequest().body(Map.of("error", "Invalid token format"));
            }

            String token = authHeader.substring(7);
            var userOpt = authService.getUserFromToken(token);

            if (userOpt.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of("error", "Invalid token"));
            }

            User user = userOpt.get();

            java.util.HashMap<String, Object> userMap = new java.util.HashMap<>();
            userMap.put("id", user.getId());
            userMap.put("email", user.getEmail());
            userMap.put("firstName", user.getFirstName());
            userMap.put("lastName", user.getLastName());
            userMap.put("role", user.getRole().name());
            userMap.put("company", user.getCompany() != null ? Map.of(
                    "id", user.getCompany().getId(),
                    "name", user.getCompany().getName(),
                    "domain", user.getCompany().getDomain()) : null);
            userMap.put("manufacturer", user.getManufacturer() != null ? Map.of(
                    "id", user.getManufacturer().getId(),
                    "name", user.getManufacturer().getName(),
                    "manufacturerId", user.getManufacturer().getManufacturerId()) : null);

            return ResponseEntity.ok(Map.of(
                    "valid", true,
                    "user", userMap));
        } catch (Exception e) {
            log.error("Token validation error: {}", e.getMessage(), e);
            return ResponseEntity.badRequest().body(Map.of(
                    "valid", false,
                    "error", e.getMessage() != null ? e.getMessage() : "Unknown error"));
        }
    }

    @GetMapping("/oauth2/success")
    @Operation(summary = "OAuth2 login success callback", description = "Handles successful OAuth2 authentication and returns JWT token", responses = {
            @ApiResponse(responseCode = "200", description = "OAuth2 login successful", content = @Content(mediaType = "application/json", schema = @Schema(example = "{\"message\": \"OAuth2 login successful\", \"token\": \"jwt-token\", \"user\": {...}, \"provider\": \"google\"}"))),
            @ApiResponse(responseCode = "400", description = "OAuth2 login failed", content = @Content(mediaType = "application/json", schema = @Schema(example = "{\"error\": \"OAuth2 login failed\", \"message\": \"Error details\"}")))
    })
    public ResponseEntity<Map<String, Object>> oauth2Success(OAuth2AuthenticationToken authentication) {
        try {
            OAuth2User oauth2User = authentication.getPrincipal();
            String email = oauth2User.getAttribute("email");
            String name = oauth2User.getAttribute("name");
            String provider = authentication.getAuthorizedClientRegistrationId();

            // Check if user exists, create if not
            var existingUser = authService.findByEmail(email);
            User user;

            if (existingUser.isEmpty()) {
                // Create new user from OAuth2 data
                String[] nameParts = name != null ? name.split(" ", 2) : new String[] { "", "" };
                String firstName = nameParts.length > 0 ? nameParts[0] : "";
                String lastName = nameParts.length > 1 ? nameParts[1] : "";

                user = authService.registerOAuth2User(
                        email,
                        firstName,
                        lastName,
                        provider);
            } else {
                user = existingUser.get();
            }

            String token = authService.generateToken(user);

            java.util.HashMap<String, Object> userMap = new java.util.HashMap<>();
            userMap.put("id", user.getId());
            userMap.put("email", user.getEmail());
            userMap.put("firstName", user.getFirstName());
            userMap.put("lastName", user.getLastName());
            userMap.put("role", user.getRole().name());
            userMap.put("company", user.getCompany() != null ? Map.of(
                    "id", user.getCompany().getId(),
                    "name", user.getCompany().getName(),
                    "domain", user.getCompany().getDomain()) : null);
            userMap.put("manufacturer", user.getManufacturer() != null ? Map.of(
                    "id", user.getManufacturer().getId(),
                    "name", user.getManufacturer().getName(),
                    "manufacturerId", user.getManufacturer().getManufacturerId()) : null);

            return ResponseEntity.ok(Map.of(
                    "message", "OAuth2 login successful",
                    "token", token,
                    "user", userMap,
                    "provider", provider));
        } catch (Exception e) {
            log.error("OAuth2 login error: {}", e.getMessage(), e);
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "OAuth2 login failed",
                    "message", e.getMessage() != null ? e.getMessage() : "Unknown error"));
        }
    }

    public static class RegisterRequest {
        private String email;
        private String password;
        private String firstName;
        private String lastName;
        private String companyName;
        private String companyDomain;

        // Getters and setters
        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }

        public String getPassword() {
            return password;
        }

        public void setPassword(String password) {
            this.password = password;
        }

        public String getFirstName() {
            return firstName;
        }

        public void setFirstName(String firstName) {
            this.firstName = firstName;
        }

        public String getLastName() {
            return lastName;
        }

        public void setLastName(String lastName) {
            this.lastName = lastName;
        }

        public String getCompanyName() {
            return companyName;
        }

        public void setCompanyName(String companyName) {
            this.companyName = companyName;
        }

        public String getCompanyDomain() {
            return companyDomain;
        }

        public void setCompanyDomain(String companyDomain) {
            this.companyDomain = companyDomain;
        }
    }

    public static class LoginRequest {
        private String email;
        private String password;

        // Getters and setters
        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }

        public String getPassword() {
            return password;
        }

        public void setPassword(String password) {
            this.password = password;
        }
    }
}