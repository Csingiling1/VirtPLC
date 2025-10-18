package com.virtplc.api;

import com.virtplc.model.AuthRequest;
import com.virtplc.model.AuthResponse;
import com.virtplc.security.JwtUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST controller for authentication and JWT token generation.
 */
@Slf4j
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class AuthController {

    private final JwtUtil jwtUtil;

    /**
     * Login endpoint - generates JWT token.
     * For demo purposes, accepts any username/password.
     * TODO: Implement proper authentication with user database.
     */
    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@RequestBody AuthRequest request) {
        log.info("Login attempt for user: {}", request.getUsername());
        
        // TODO: Validate credentials against user database
        // For now, accept any non-empty username/password
        if (request.getUsername() != null && !request.getUsername().isEmpty() &&
            request.getPassword() != null && !request.getPassword().isEmpty()) {
            
            String token = jwtUtil.generateToken(request.getUsername());
            AuthResponse response = new AuthResponse(
                token,
                request.getUsername(),
                "Login successful"
            );
            
            log.info("Login successful for user: {}", request.getUsername());
            return ResponseEntity.ok(response);
        }
        
        log.warn("Login failed for user: {}", request.getUsername());
        return ResponseEntity.badRequest()
                .body(new AuthResponse(null, null, "Invalid credentials"));
    }

    /**
     * Validate token endpoint.
     */
    @GetMapping("/validate")
    public ResponseEntity<String> validateToken(@RequestHeader("Authorization") String authHeader) {
        try {
            if (authHeader != null && authHeader.startsWith("Bearer ")) {
                String token = authHeader.substring(7);
                String username = jwtUtil.extractUsername(token);
                
                if (username != null && !jwtUtil.isTokenExpired(token)) {
                    return ResponseEntity.ok("Token is valid for user: " + username);
                }
            }
            return ResponseEntity.badRequest().body("Invalid token");
        } catch (Exception e) {
            log.error("Token validation error", e);
            return ResponseEntity.badRequest().body("Token validation failed");
        }
    }
}
