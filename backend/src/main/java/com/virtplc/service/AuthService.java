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
        log.debug("Attempting to register user: {}", email);
        // Check if user already exists
        if (userRepository.findByEmail(email).isPresent()) {
            log.debug("User already exists: {}", email);
            throw new RuntimeException("User already exists with this email");
        }

        // Find or create company
        Company company = companyRepository.findByDomain(companyDomain)
                .orElseGet(() -> {
                    log.debug("Creating new company: {} with domain: {}", companyName, companyDomain);
                    Company newCompany = Company.builder()
                            .name(companyName)
                            .domain(companyDomain)
                            .displayName(companyName)
                            .active(true)
                            .build();
                    return companyRepository.save(newCompany);
                });

        // Create user - first user of company becomes ADMIN, others become
        // MANUFACTURER_ADMIN
        long companyUserCount = userRepository.countByCompanyId(company.getId());
        User.Role userRole = (companyUserCount == 0) ? User.Role.ADMIN : User.Role.MANUFACTURER_ADMIN;

        User user = User.builder()
                .email(email)
                .password(passwordEncoder.encode(password))
                .firstName(firstName)
                .lastName(lastName)
                .role(userRole)
                .company(company)
                .manufacturer(null) // Will be assigned later when linking to manufacturer
                .active(true)
                .build();

        User savedUser = userRepository.save(user);
        log.info("Registered new user: {} for company: {} with role: {}", email, companyName, userRole);
        return savedUser;
    }

    public Optional<User> authenticateUser(String email, String password) {
        log.debug("Attempting to authenticate user: {}", email);
        Optional<User> userOpt = userRepository.findByEmail(email);
        if (userOpt.isPresent()) {
            User user = userOpt.get();
            log.debug("User found: {}, active: {}", email, user.isActive());
            boolean passwordMatches = passwordEncoder.matches(password, user.getPassword());
            log.debug("Password matches: {}", passwordMatches);
            if (passwordMatches && user.isActive()) {
                log.debug("Authentication successful for user: {}", email);
                return Optional.of(user);
            } else {
                log.debug("Authentication failed for user: {} - password match: {}, active: {}", email, passwordMatches,
                        user.isActive());
            }
        } else {
            log.debug("User not found: {}", email);
        }
        return Optional.empty();
    }

    @Transactional
    public User registerOAuth2User(String email, String firstName, String lastName, String provider) {
        log.debug("Attempting to register OAuth2 user: {} from provider: {}", email, provider);

        // Check if user already exists
        Optional<User> existingUser = userRepository.findByEmail(email);
        if (existingUser.isPresent()) {
            log.debug("OAuth2 user already exists: {}", email);
            return existingUser.get();
        }

        // Create a default company for OAuth2 users
        String companyDomain = email.split("@")[1] + "-oauth2";
        Company company = companyRepository.findByDomain(companyDomain)
                .orElseGet(() -> {
                    log.debug("Creating new OAuth2 company: {} for domain: {}", provider + " Users", companyDomain);
                    Company newCompany = Company.builder()
                            .name(provider + " Users")
                            .domain(companyDomain)
                            .displayName(provider + " OAuth2 Users")
                            .active(true)
                            .build();
                    return companyRepository.save(newCompany);
                });

        // Create user - first user of company becomes ADMIN, others become
        // MANUFACTURER_ADMIN
        long companyUserCount = userRepository.countByCompanyId(company.getId());
        User.Role userRole = (companyUserCount == 0) ? User.Role.ADMIN : User.Role.MANUFACTURER_ADMIN;

        User user = User.builder()
                .email(email)
                .password(passwordEncoder.encode("oauth2-" + System.currentTimeMillis())) // Random password for OAuth2
                                                                                          // users
                .firstName(firstName)
                .lastName(lastName)
                .role(userRole)
                .company(company)
                .manufacturer(null)
                .active(true)
                .build();

        User savedUser = userRepository.save(user);
        log.info("Registered new OAuth2 user: {} from provider: {} for company: {} with role: {}", email, provider,
                company.getName(), userRole);
        return savedUser;
    }

    public Optional<User> findByEmail(String email) {
        return userRepository.findByEmail(email);
    }

    public String generateToken(User user) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + jwtExpiration);

        return Jwts.builder()
                .subject(user.getEmail())
                .claim("userId", user.getId())
                .claim("companyId", user.getCompany() != null ? user.getCompany().getId() : null)
                .claim("role", user.getRole().name())
                .claim("companyDomain", user.getCompany() != null ? user.getCompany().getDomain() : null)
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