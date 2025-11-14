package com.virtplc.deployment;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * REST controller for deployment management
 * Provides endpoints for deployment tracking and rollback operations
 */
@RestController
@RequestMapping("/api/deployments")
@RequiredArgsConstructor
public class DeploymentController {

    private final DeploymentService deploymentService;

    /**
     * Record a successful deployment
     */
    @PostMapping("/record")
    public ResponseEntity<Void> recordDeployment(@RequestBody DeploymentRequest request) {
        deploymentService.recordDeployment(
                request.getVersion(),
                request.getEnvironment(),
                request.getDeploymentType());
        return ResponseEntity.ok().build();
    }

    /**
     * Record a failed deployment
     */
    @PostMapping("/record-failed")
    public ResponseEntity<Void> recordFailedDeployment(@RequestBody FailedDeploymentRequest request) {
        deploymentService.recordFailedDeployment(
                request.getVersion(),
                request.getEnvironment(),
                request.getDeploymentType(),
                request.getError());
        return ResponseEntity.ok().build();
    }

    /**
     * Perform rollback to specified version
     */
    @PostMapping("/rollback")
    public ResponseEntity<DeploymentService.RollbackResult> rollback(@RequestBody RollbackRequest request) {
        DeploymentService.RollbackResult result = deploymentService.rollback(
                request.getEnvironment(),
                request.getTargetVersion());
        return ResponseEntity.ok(result);
    }

    /**
     * Get deployment history for environment
     */
    @GetMapping("/history/{environment}")
    public ResponseEntity<List<DeploymentService.DeploymentRecord>> getDeploymentHistory(
            @PathVariable String environment) {
        List<DeploymentService.DeploymentRecord> history = deploymentService.getDeploymentHistory(environment);
        return ResponseEntity.ok(history);
    }

    /**
     * Get latest successful deployment for environment
     */
    @GetMapping("/latest/{environment}")
    public ResponseEntity<DeploymentService.DeploymentRecord> getLatestSuccessfulDeployment(
            @PathVariable String environment) {
        DeploymentService.DeploymentRecord latest = deploymentService.getLatestSuccessfulDeployment(environment);
        if (latest != null) {
            return ResponseEntity.ok(latest);
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Create backup before deployment
     */
    @PostMapping("/backup")
    public ResponseEntity<Boolean> createBackup(@RequestBody BackupRequest request) {
        boolean success = deploymentService.createBackup(request.getVersion(), request.getEnvironment());
        return ResponseEntity.ok(success);
    }

    /**
     * Clean up old backups
     */
    @PostMapping("/cleanup-backups")
    public ResponseEntity<Void> cleanupBackups() {
        deploymentService.cleanupOldBackups();
        return ResponseEntity.ok().build();
    }

    // Request DTOs

    public static class DeploymentRequest {
        private String version;
        private String environment;
        private String deploymentType;

        public String getVersion() {
            return version;
        }

        public void setVersion(String version) {
            this.version = version;
        }

        public String getEnvironment() {
            return environment;
        }

        public void setEnvironment(String environment) {
            this.environment = environment;
        }

        public String getDeploymentType() {
            return deploymentType;
        }

        public void setDeploymentType(String deploymentType) {
            this.deploymentType = deploymentType;
        }
    }

    public static class FailedDeploymentRequest extends DeploymentRequest {
        private String error;

        public String getError() {
            return error;
        }

        public void setError(String error) {
            this.error = error;
        }
    }

    public static class RollbackRequest {
        private String environment;
        private String targetVersion;

        public String getEnvironment() {
            return environment;
        }

        public void setEnvironment(String environment) {
            this.environment = environment;
        }

        public String getTargetVersion() {
            return targetVersion;
        }

        public void setTargetVersion(String targetVersion) {
            this.targetVersion = targetVersion;
        }
    }

    public static class BackupRequest {
        private String version;
        private String environment;

        public String getVersion() {
            return version;
        }

        public void setVersion(String version) {
            this.version = version;
        }

        public String getEnvironment() {
            return environment;
        }

        public void setEnvironment(String environment) {
            this.environment = environment;
        }
    }
}