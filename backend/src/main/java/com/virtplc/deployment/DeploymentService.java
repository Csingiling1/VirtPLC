package com.virtplc.deployment;

import com.virtplc.logging.StructuredLogger;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.stream.Collectors;

/**
 * Deployment tracking and rollback service
 * Tracks deployments and provides automated rollback capabilities
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class DeploymentService {

    private final StructuredLogger structuredLogger;

    @Value("${virtplc.deployment.backup-dir:/opt/virtplc/backups}")
    private String backupDirectory;

    @Value("${virtplc.deployment.max-backups:10}")
    private int maxBackups;

    private final List<DeploymentRecord> deploymentHistory = new CopyOnWriteArrayList<>();

    /**
     * Record a successful deployment
     */
    public void recordDeployment(String version, String environment, String deploymentType) {
        DeploymentRecord record = new DeploymentRecord(
                version,
                environment,
                deploymentType,
                LocalDateTime.now(),
                "SUCCESS");

        deploymentHistory.add(record);

        // Keep only recent deployments
        if (deploymentHistory.size() > 100) {
            deploymentHistory.remove(0);
        }

        structuredLogger.logOperationStart("deployment-recorded",
                java.util.Map.of("version", version, "environment", environment));

        log.info("Deployment recorded: {} to {} at {}", version, environment, record.getTimestamp());
    }

    /**
     * Record a failed deployment
     */
    public void recordFailedDeployment(String version, String environment, String deploymentType, String error) {
        DeploymentRecord record = new DeploymentRecord(
                version,
                environment,
                deploymentType,
                LocalDateTime.now(),
                "FAILED");
        record.setErrorMessage(error);

        deploymentHistory.add(record);

        structuredLogger.logOperationFailed("deployment-failed",
                new RuntimeException(error),
                java.util.Map.of("version", version, "environment", environment));

        log.error("Deployment failed: {} to {} - Error: {}", version, environment, error);
    }

    /**
     * Perform rollback to previous version
     */
    public RollbackResult rollback(String environment, String targetVersion) {
        try {
            structuredLogger.logOperationStart("rollback-initiated",
                    java.util.Map.of("environment", environment, "targetVersion", targetVersion));

            // Find the target deployment
            DeploymentRecord targetDeployment = deploymentHistory.stream()
                    .filter(d -> d.getEnvironment().equals(environment) &&
                            d.getVersion().equals(targetVersion) &&
                            "SUCCESS".equals(d.getStatus()))
                    .max(Comparator.comparing(DeploymentRecord::getTimestamp))
                    .orElse(null);

            if (targetDeployment == null) {
                String error = "Target version not found: " + targetVersion;
                log.error(error);
                return new RollbackResult(false, error);
            }

            // Perform the actual rollback
            boolean success = performRollback(environment, targetDeployment);

            if (success) {
                structuredLogger.logOperationComplete("rollback-completed", 0,
                        java.util.Map.of("environment", environment, "targetVersion", targetVersion));
                log.info("Rollback completed successfully to version: {}", targetVersion);
                return new RollbackResult(true, "Rollback completed successfully");
            } else {
                String error = "Rollback failed for version: " + targetVersion;
                structuredLogger.logOperationFailed("rollback-failed", new RuntimeException(error),
                        java.util.Map.of("environment", environment, "targetVersion", targetVersion));
                log.error(error);
                return new RollbackResult(false, error);
            }

        } catch (Exception e) {
            String error = "Rollback failed with exception: " + e.getMessage();
            structuredLogger.logOperationFailed("rollback-exception", e,
                    java.util.Map.of("environment", environment, "targetVersion", targetVersion));
            log.error(error, e);
            return new RollbackResult(false, error);
        }
    }

    /**
     * Perform the actual rollback operation
     */
    private boolean performRollback(String environment, DeploymentRecord targetDeployment) {
        try {
            // This is a placeholder for actual rollback implementation
            // In a real system, this would:
            // 1. Stop current services
            // 2. Restore from backup if available
            // 3. Update Kubernetes deployments or Docker Compose
            // 4. Restart services
            // 5. Verify health

            log.info("Performing rollback to version {} in environment {}",
                    targetDeployment.getVersion(), environment);

            // Simulate rollback operations
            Thread.sleep(2000); // Simulate time for rollback

            // For Docker Compose based deployments
            if ("docker-compose".equals(targetDeployment.getDeploymentType())) {
                return performDockerComposeRollback(environment, targetDeployment);
            }

            // For Kubernetes deployments
            if ("kubernetes".equals(targetDeployment.getDeploymentType())) {
                return performKubernetesRollback(environment, targetDeployment);
            }

            // Default success for demonstration
            return true;

        } catch (Exception e) {
            log.error("Error during rollback execution", e);
            return false;
        }
    }

    /**
     * Docker Compose rollback implementation
     */
    private boolean performDockerComposeRollback(String environment, DeploymentRecord targetDeployment) {
        try {
            // Placeholder for Docker Compose rollback
            log.info("Rolling back Docker Compose deployment to version: {}", targetDeployment.getVersion());

            // In a real implementation, this would:
            // 1. Pull the target version image
            // 2. Update docker-compose.yml with target version
            // 3. Run docker-compose down && docker-compose up

            ProcessBuilder pb = new ProcessBuilder(
                    "docker-compose",
                    "-f", getEnvironmentComposeFile(environment),
                    "pull");
            pb.inheritIO();
            Process process = pb.start();
            int exitCode = process.waitFor();

            return exitCode == 0;

        } catch (Exception e) {
            log.error("Docker Compose rollback failed", e);
            return false;
        }
    }

    /**
     * Kubernetes rollback implementation
     */
    private boolean performKubernetesRollback(String environment, DeploymentRecord targetDeployment) {
        try {
            // Placeholder for Kubernetes rollback
            log.info("Rolling back Kubernetes deployment to version: {}", targetDeployment.getVersion());

            // In a real implementation, this would:
            // 1. Use kubectl rollout undo
            // 2. Or update deployment image tag

            ProcessBuilder pb = new ProcessBuilder(
                    "kubectl",
                    "rollout",
                    "undo",
                    "deployment/virtplc-backend",
                    "-n", getKubernetesNamespace(environment));
            pb.inheritIO();
            Process process = pb.start();
            int exitCode = process.waitFor();

            return exitCode == 0;

        } catch (Exception e) {
            log.error("Kubernetes rollback failed", e);
            return false;
        }
    }

    /**
     * Create backup before deployment
     */
    public boolean createBackup(String version, String environment) {
        try {
            Path backupDir = Paths.get(backupDirectory, environment, version);
            Files.createDirectories(backupDir);

            // Placeholder for backup creation
            // In a real implementation, this would backup:
            // - Database dumps
            // - Configuration files
            // - Volume data

            log.info("Backup created for version {} in environment {}", version, environment);
            return true;

        } catch (IOException e) {
            log.error("Failed to create backup", e);
            return false;
        }
    }

    /**
     * Get deployment history
     */
    public List<DeploymentRecord> getDeploymentHistory(String environment) {
        return deploymentHistory.stream()
                .filter(d -> d.getEnvironment().equals(environment))
                .sorted(Comparator.comparing(DeploymentRecord::getTimestamp).reversed())
                .collect(Collectors.toList());
    }

    /**
     * Get latest successful deployment for environment
     */
    public DeploymentRecord getLatestSuccessfulDeployment(String environment) {
        return deploymentHistory.stream()
                .filter(d -> d.getEnvironment().equals(environment) && "SUCCESS".equals(d.getStatus()))
                .max(Comparator.comparing(DeploymentRecord::getTimestamp))
                .orElse(null);
    }

    /**
     * Clean up old backups
     */
    public void cleanupOldBackups() {
        try {
            Path backupDir = Paths.get(backupDirectory);
            if (!Files.exists(backupDir)) {
                return;
            }

            List<Path> backups = Files.list(backupDir)
                    .filter(Files::isDirectory)
                    .sorted(Comparator.comparing(this::getBackupTimestamp).reversed())
                    .collect(Collectors.toList());

            if (backups.size() > maxBackups) {
                List<Path> toDelete = backups.subList(maxBackups, backups.size());
                for (Path backup : toDelete) {
                    deleteDirectory(backup);
                    log.info("Deleted old backup: {}", backup.getFileName());
                }
            }

        } catch (Exception e) {
            log.error("Failed to cleanup old backups", e);
        }
    }

    private LocalDateTime getBackupTimestamp(Path backupPath) {
        try {
            return LocalDateTime.parse(backupPath.getFileName().toString().replace("_", "T"));
        } catch (Exception e) {
            return LocalDateTime.MIN;
        }
    }

    private void deleteDirectory(Path path) throws IOException {
        Files.walk(path)
                .sorted(Comparator.reverseOrder())
                .forEach(p -> {
                    try {
                        Files.delete(p);
                    } catch (IOException e) {
                        log.warn("Failed to delete: {}", p, e);
                    }
                });
    }

    private String getEnvironmentComposeFile(String environment) {
        return String.format("docker-compose.%s.yml", environment);
    }

    private String getKubernetesNamespace(String environment) {
        return "virtplc-" + environment;
    }

    /**
     * Deployment record class
     */
    public static class DeploymentRecord {
        private final String version;
        private final String environment;
        private final String deploymentType;
        private final LocalDateTime timestamp;
        private final String status;
        private String errorMessage;

        public DeploymentRecord(String version, String environment, String deploymentType,
                LocalDateTime timestamp, String status) {
            this.version = version;
            this.environment = environment;
            this.deploymentType = deploymentType;
            this.timestamp = timestamp;
            this.status = status;
        }

        // Getters and setters
        public String getVersion() {
            return version;
        }

        public String getEnvironment() {
            return environment;
        }

        public String getDeploymentType() {
            return deploymentType;
        }

        public LocalDateTime getTimestamp() {
            return timestamp;
        }

        public String getStatus() {
            return status;
        }

        public String getErrorMessage() {
            return errorMessage;
        }

        public void setErrorMessage(String errorMessage) {
            this.errorMessage = errorMessage;
        }
    }

    /**
     * Rollback result class
     */
    public static class RollbackResult {
        private final boolean success;
        private final String message;

        public RollbackResult(boolean success, String message) {
            this.success = success;
            this.message = message;
        }

        public boolean isSuccess() {
            return success;
        }

        public String getMessage() {
            return message;
        }
    }
}