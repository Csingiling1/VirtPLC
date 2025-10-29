package com.virtplc.service;

import com.virtplc.model.Company;
import com.virtplc.model.User;
import com.virtplc.repository.CompanyRepository;
import com.virtplc.repository.UserRepository;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.crypto.SecretKey;
import java.time.LocalDateTime;
import java.util.Date;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class AuthService {

    private final UserRepository userRepository;
    private final CompanyRepository companyRepository;
    private final PasswordEncoder passwordEncoder;

    @Value("${jwt.secret:virtplc-secret-key-for-jwt-tokens-that-should-be-at-least-512-bits-long}")
    private String jwtSecret;

    @Value("${jwt.expiration:86400000}") // 24 hours in milliseconds
    private long jwtExpiration;

    private SecretKey getSigningKey() {
        return Keys.hmacShaKeyFor(jwtSecret.getBytes());
    }

    @Transactional
    public User registerUser(String email, String password, String firstName, String lastName,
            String companyName, String companyDomain) {
        // Check if user already exists
        if (userRepository.findByEmail(email).isPresent()) {
            throw new RuntimeException("User already exists with this email");
        }

        // Find or create company
        Company company = companyRepository.findByDomain(companyDomain)
                .orElseGet(() -> {
                    Company newCompany = Company.builder()
                            .name(companyName)
                            .domain(companyDomain)
                            .displayName(companyName)
                            .active(true)
                            .build();
                    return companyRepository.save(newCompany);
                });

        // Create user
        User user = User.builder()
                .email(email)
                .password(passwordEncoder.encode(password))
                .firstName(firstName)
                .lastName(lastName)
                .role(User.Role.ADMIN) // First user of company is admin
                .company(company)
                .active(true)
                .build();

        User savedUser = userRepository.save(user);
        log.info("Registered new user: {} for company: {}", email, companyName);
        return savedUser;
    }

    public Optional<User> authenticateUser(String email, String password) {
        Optional<User> userOpt = userRepository.findByEmail(email);
        if (userOpt.isPresent()) {
            User user = userOpt.get();
            if (passwordEncoder.matches(password, user.getPassword()) && user.isActive()) {
                return Optional.of(user);
            }
        }
        return Optional.empty();
    }

    public String generateToken(User user) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + jwtExpiration);

        return Jwts.builder()
                .subject(user.getEmail())
                .claim("userId", user.getId())
                .claim("companyId", user.getCompany().getId())
                .claim("role", user.getRole().name())
                .claim("companyDomain", user.getCompany().getDomain())
                .issuedAt(now)
                .expiration(expiryDate)
                .signWith(getSigningKey())
                .compact();
    }

    public Optional<User> getUserFromToken(String token) {
        try {
            String email = Jwts.parser()
                    .verifyWith(getSigningKey())
                    .build()
                    .parseSignedClaims(token)
                    .getPayload()
                    .getSubject();

            return userRepository.findByEmail(email);
        } catch (Exception e) {
            log.error("Error parsing JWT token: {}", e.getMessage());
            return Optional.empty();
        }
    }

    public boolean validateToken(String token) {
        try {
            Jwts.parser()
                    .verifyWith(getSigningKey())
                    .build()
                    .parseSignedClaims(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}