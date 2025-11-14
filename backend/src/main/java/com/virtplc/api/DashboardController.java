package com.virtplc.api;

import com.virtplc.model.Dashboard;
import com.virtplc.model.User;
import com.virtplc.service.DashboardService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * REST API for dashboard management
 */
@RestController
@RequestMapping("/api/dashboards")
@RequiredArgsConstructor
@Slf4j
public class DashboardController {

    private final DashboardService dashboardService;

    /**
     * Get all dashboards for the current user
     */
    @GetMapping
    public ResponseEntity<List<Dashboard>> getUserDashboards() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        if (authentication == null || !(authentication.getPrincipal() instanceof User)) {
            return ResponseEntity.status(401).build();
        }

        User user = (User) authentication.getPrincipal();
        List<Dashboard> dashboards = dashboardService.getUserDashboards(String.valueOf(user.getId()));
        return ResponseEntity.ok(dashboards);
    }

    /**
     * Get dashboard by ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<Dashboard> getDashboard(@PathVariable Long id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        if (authentication == null || !(authentication.getPrincipal() instanceof User)) {
            return ResponseEntity.status(401).build();
        }

        User user = (User) authentication.getPrincipal();
        Optional<Dashboard> dashboard = dashboardService.getDashboard(id, String.valueOf(user.getId()));

        return dashboard.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Create new dashboard
     */
    @PostMapping
    public ResponseEntity<Dashboard> createDashboard(@RequestBody Dashboard dashboard) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        if (authentication == null || !(authentication.getPrincipal() instanceof User)) {
            return ResponseEntity.status(401).build();
        }

        User user = (User) authentication.getPrincipal();
        dashboard.setUserId(String.valueOf(user.getId()));

        Optional<Dashboard> created = dashboardService.createDashboard(dashboard);
        return created.map(ResponseEntity::ok)
                .orElse(ResponseEntity.badRequest().build());
    }

    /**
     * Update dashboard
     */
    @PutMapping("/{id}")
    public ResponseEntity<Dashboard> updateDashboard(
            @PathVariable Long id,
            @RequestBody Dashboard dashboard) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        if (authentication == null || !(authentication.getPrincipal() instanceof User)) {
            return ResponseEntity.status(401).build();
        }

        User user = (User) authentication.getPrincipal();
        dashboard.setId(id);
        dashboard.setUserId(String.valueOf(user.getId()));

        Optional<Dashboard> updated = dashboardService.updateDashboard(dashboard);
        return updated.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Delete dashboard
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteDashboard(@PathVariable Long id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        if (authentication == null || !(authentication.getPrincipal() instanceof User)) {
            return ResponseEntity.status(401).build();
        }

        User user = (User) authentication.getPrincipal();
        boolean deleted = dashboardService.deleteDashboard(id, String.valueOf(user.getId()));

        return deleted ? ResponseEntity.noContent().build()
                : ResponseEntity.notFound().build();
    }

    /**
     * Share dashboard (make it public)
     */
    @PostMapping("/{id}/share")
    public ResponseEntity<Map<String, Object>> shareDashboard(@PathVariable Long id) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        if (authentication == null || !(authentication.getPrincipal() instanceof User)) {
            return ResponseEntity.status(401).build();
        }

        User user = (User) authentication.getPrincipal();
        boolean shared = dashboardService.shareDashboard(id, String.valueOf(user.getId()));

        if (shared) {
            Map<String, Object> response = Map.of(
                    "success", true,
                    "message", "Dashboard shared successfully");
            return ResponseEntity.ok(response);
        } else {
            Map<String, Object> response = Map.of(
                    "success", false,
                    "message", "Dashboard not found");
            return ResponseEntity.status(404).body(response);
        }
    }
}