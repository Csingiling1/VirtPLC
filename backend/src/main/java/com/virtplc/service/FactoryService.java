package com.virtplc.service;

import com.virtplc.model.Factory;
import com.virtplc.model.User;
import com.virtplc.repository.FactoryRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class FactoryService {

    private final FactoryRepository factoryRepository;

    /**
     * Get all factories visible to a user based on their role and permissions.
     * - ADMIN: sees all factories
     * - MANUFACTURER_ADMIN: sees all factories in their manufacturer
     * - Other roles: sees all factories in their manufacturer (default behavior)
     */
    @Transactional(readOnly = true)
    public List<Factory> getFactoriesForUser(User user) {
        if (user.getRole() == User.Role.ADMIN) {
            // Admin sees all factories
            return factoryRepository.findAll();
        } else if (user.getManufacturer() != null) {
            // User with manufacturer sees only their manufacturer's factories
            return factoryRepository.findByManufacturerId(user.getManufacturer().getId());
        } else {
            // User without manufacturer sees no factories
            return List.of();
        }
    }

    /**
     * Get a specific factory if the user has permission to view it.
     */
    @Transactional(readOnly = true)
    public Optional<Factory> getFactoryForUser(String factoryId, User user) {
        Optional<Factory> factoryOpt = factoryRepository.findByFactoryId(factoryId);

        if (factoryOpt.isEmpty()) {
            return Optional.empty();
        }

        Factory factory = factoryOpt.get();

        // Check permissions
        if (user.getRole() == User.Role.ADMIN) {
            // Admin can see any factory
            return factoryOpt;
        } else if (user.getManufacturer() != null) {
            // User can see factory if it belongs to their manufacturer
            if (factory.getManufacturer() != null &&
                    factory.getManufacturer().getId().equals(user.getManufacturer().getId())) {
                return factoryOpt;
            }
        }

        return Optional.empty();
    }
}
