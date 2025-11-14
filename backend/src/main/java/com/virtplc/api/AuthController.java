package com.virtplc.api;

import com.virtplc.model.User;
import com.virtplc.service.AuthService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class AuthController {

    private final AuthService authService;

    @PostMapping("/register")
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