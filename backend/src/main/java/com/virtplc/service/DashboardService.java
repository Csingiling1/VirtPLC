package com.virtplc.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.virtplc.model.Dashboard;
import com.virtplc.repository.DashboardRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Service for dashboard management
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class DashboardService {

    private final DashboardRepository dashboardRepository;
    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Get all dashboards for a user
     */
    public List<Dashboard> getUserDashboards(String userId) {
        List<Dashboard> dashboards = dashboardRepository.findByUserId(userId);
        // Convert JSON to items for each dashboard
        dashboards.forEach(this::populateItemsFromJson);
        return dashboards;
    }

    /**
     * Get dashboard by ID and user ID
     */
    public Optional<Dashboard> getDashboard(Long id, String userId) {
        Optional<Dashboard> dashboard = dashboardRepository.findByIdAndUserId(id, userId);
        dashboard.ifPresent(this::populateItemsFromJson);
        return dashboard;
    }

    /**
     * Create a new dashboard
     */
    public Optional<Dashboard> createDashboard(Dashboard dashboard) {
        try {
            // Convert items to JSON
            dashboard.setItemsJson(objectMapper.writeValueAsString(dashboard.getItems()));
            dashboard.setCreatedAt(LocalDateTime.now());
            dashboard.setUpdatedAt(LocalDateTime.now());
            dashboard.setIsPublic(false);

            Dashboard saved = dashboardRepository.save(dashboard);
            // Populate items from JSON for return
            populateItemsFromJson(saved);
            log.info("Created dashboard: {} for user: {}", saved.getId(), saved.getUserId());
            return Optional.of(saved);
        } catch (Exception e) {
            log.error("Error creating dashboard", e);
            return Optional.empty();
        }
    }

    /**
     * Update an existing dashboard
     */
    public Optional<Dashboard> updateDashboard(Dashboard dashboard) {
        try {
            Optional<Dashboard> existing = dashboardRepository.findByIdAndUserId(dashboard.getId(),
                    dashboard.getUserId());
            if (existing.isEmpty()) {
                return Optional.empty();
            }

            // Convert items to JSON
            dashboard.setItemsJson(objectMapper.writeValueAsString(dashboard.getItems()));
            dashboard.setUpdatedAt(LocalDateTime.now());
            Dashboard saved = dashboardRepository.save(dashboard);
            // Populate items from JSON for return
            populateItemsFromJson(saved);
            log.info("Updated dashboard: {} for user: {}", saved.getId(), saved.getUserId());
            return Optional.of(saved);
        } catch (Exception e) {
            log.error("Error updating dashboard", e);
            return Optional.empty();
        }
    }

    /**
     * Delete a dashboard
     */
    public boolean deleteDashboard(Long id, String userId) {
        try {
            Optional<Dashboard> existing = dashboardRepository.findByIdAndUserId(id, userId);
            if (existing.isEmpty()) {
                return false;
            }

            dashboardRepository.deleteById(id);
            log.info("Deleted dashboard: {} for user: {}", id, userId);
            return true;
        } catch (Exception e) {
            log.error("Error deleting dashboard", e);
            return false;
        }
    }

    /**
     * Share a dashboard (make it public)
     */
    public boolean shareDashboard(Long id, String userId) {
        try {
            Optional<Dashboard> existing = dashboardRepository.findByIdAndUserId(id, userId);
            if (existing.isEmpty()) {
                return false;
            }

            Dashboard dashboard = existing.get();
            dashboard.setIsPublic(true);
            dashboard.setUpdatedAt(LocalDateTime.now());
            dashboardRepository.save(dashboard);

            log.info("Shared dashboard: {} for user: {}", id, userId);
            return true;
        } catch (Exception e) {
            log.error("Error sharing dashboard", e);
            return false;
        }
    }

    /**
     * Get public dashboards
     */
    public List<Dashboard> getPublicDashboards() {
        List<Dashboard> dashboards = dashboardRepository.findByIsPublic(true);
        dashboards.forEach(this::populateItemsFromJson);
        return dashboards;
    }

    /**
     * Helper method to populate items from JSON
     */
    private void populateItemsFromJson(Dashboard dashboard) {
        if (dashboard.getItemsJson() != null && !dashboard.getItemsJson().isEmpty()) {
            try {
                List<Dashboard.CanvasItem> items = objectMapper.readValue(
                        dashboard.getItemsJson(),
                        new TypeReference<List<Dashboard.CanvasItem>>() {
                        });
                dashboard.setItems(items);
            } catch (Exception e) {
                log.error("Error parsing items JSON for dashboard {}", dashboard.getId(), e);
                dashboard.setItems(List.of());
            }
        } else {
            dashboard.setItems(List.of());
        }
    }
}