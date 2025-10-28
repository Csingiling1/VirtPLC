package com.virtplc.service;

import com.virtplc.model.User;
import com.virtplc.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

/**
 * Service for user management and authentication
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    /**
     * Create a new user with encoded password
     */
    @Transactional
    public User createUser(String username, String password, String email) {
        log.info("Creating new user: {}", username);

        if (userRepository.existsByUsername(username)) {
            throw new RuntimeException("Username already exists: " + username);
        }

        if (userRepository.existsByEmail(email)) {
            throw new RuntimeException("Email already exists: " + email);
        }

        User user = User.builder()
                .username(username)
                .password(passwordEncoder.encode(password))
                .email(email)
                .role("USER")
                .enabled(true)
                .build();

        return userRepository.save(user);
    }

    /**
     * Find user by username
     */
    public Optional<User> findByUsername(String username) {
        return userRepository.findByUsername(username);
    }

    /**
     * Validate user credentials
     */
    public boolean validateCredentials(String username, String password) {
        Optional<User> user = userRepository.findByUsername(username);
        if (user.isPresent() && user.get().isEnabled()) {
            return passwordEncoder.matches(password, user.get().getPassword());
        }
        return false;
    }

    /**
     * Create default admin user if not exists
     */
    @Transactional
    public void createDefaultAdminUser() {
        if (!userRepository.existsByUsername("admin")) {
            log.info("Creating default admin user");
            createUser("admin", "admin123", "admin@virtplc.com");
        }
    }
}