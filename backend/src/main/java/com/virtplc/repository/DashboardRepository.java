package com.virtplc.repository;

import com.virtplc.model.Dashboard;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository for dashboard persistence
 */
@Repository
public interface DashboardRepository extends JpaRepository<Dashboard, Long> {

    /**
     * Find all dashboards for a user
     */
    List<Dashboard> findByUserId(String userId);

    /**
     * Find dashboard by ID and user ID
     */
    Optional<Dashboard> findByIdAndUserId(Long id, String userId);

    /**
     * Find public dashboards
     */
    List<Dashboard> findByIsPublic(boolean isPublic);
}