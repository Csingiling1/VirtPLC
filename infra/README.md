# VirtPLC Kubernetes Infrastructure

This directory contains the complete Kubernetes infrastructure for deploying VirtPLC as a multi-tenant, production-ready application.

## Architecture Overview

The VirtPLC platform is deployed using a multi-tenant architecture with:

- **Global Components**: Shared services (Frontend, AI Service, Monitoring) in `virtplc-system` namespace
- **Factory Components**: Isolated per-manufacturer deployments in separate namespaces
- **Monitoring Stack**: Prometheus, Grafana, and Loki for centralized observability
- **Ingress**: NGINX ingress controller for multi-tenant routing

## Directory Structure

```bash
infra/
├── helm/
│   ├── factory-chart/          # Helm chart for factory deployments
│   │   ├── Chart.yaml         # Chart metadata and dependencies
│   │   ├── values.yaml        # Default configuration values
│   │   ├── templates/         # Kubernetes resource templates
│   │   └── tests/             # Helm test templates
│   └── global/                # Helm chart for global components
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── templates/
│       └── dashboards/
└── k8s/                       # Static Kubernetes manifests
    ├── ingress.yaml          # NGINX ingress configuration
    ├── namespaces.yaml       # Namespace definitions
    ├── network-policies.yaml # Network security policies
    ├── secrets.yaml          # Secret templates
    └── services.yaml         # Service definitions
```

## Prerequisites

- Kubernetes cluster (K3s recommended for on-prem)
- Helm 3.x
- kubectl configured
- NGINX Ingress Controller
- cert-manager (for TLS certificates)
- Storage class for persistent volumes

## Quick Start

### 1. Install Global Components

```bash
# Add Helm repositories
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install global components
helm install virtplc-global ./infra/helm/global \
  --namespace virtplc-system \
  --create-namespace \
  --set global.registry=ghcr.io \
  --set global.imageTag=latest
```

### 2. Provision a Factory

```bash
# Using GitHub Actions (recommended)
# Trigger the "Factory Provisioning" workflow with:
# - factory_name: "factory-a"
# - factory_timezone: "America/New_York"
# - database_size: "10Gi"
# - environment: "production"

# Or manually with Helm
helm install factory-a ./infra/helm/factory-chart \
  --namespace virtplc-factory-a \
  --create-namespace \
  --set factory.name=factory-a \
  --set factory.timezone=America/New_York \
  --set postgresql.persistence.size=10Gi
```

### 3. Access the Application

- **Frontend**: `https://virtplc.example.com`
- **Factory API**: `https://virtplc.example.com/api/factory/{factory-name}`
- **Monitoring**: `https://virtplc.example.com/monitoring`
- **Grafana**: `https://virtplc.example.com/monitoring` (admin/admin)

## Configuration

### Factory Configuration

Each factory can be customized via Helm values:

```yaml
factory:
  name: "factory-a"              # Unique factory identifier
  timezone: "America/New_York"   # Factory timezone

backend:
  replicaCount: 2                # Number of backend replicas
  resources:
    limits:
      cpu: 1000m
      memory: 2Gi
    requests:
      cpu: 500m
      memory: 1Gi

postgresql:
  persistence:
    size: 10Gi                  # Database storage size
```

### Global Configuration

Global components are configured in `infra/helm/global/values.yaml`:

```yaml
frontend:
  enabled: true
  replicaCount: 2

aiService:
  enabled: true
  replicaCount: 1

prometheus:
  enabled: true

grafana:
  enabled: true
  adminPassword: "admin"
```

## Security

### Network Policies

- Factory isolation: Each factory namespace is isolated from others
- Global access: Global services can communicate with all factories
- Monitoring access: Monitoring stack can collect metrics from all namespaces

### Secrets Management

- Database passwords are auto-generated per factory
- JWT secrets are unique per factory
- TLS certificates managed by cert-manager

## Monitoring

### Metrics Collected

- Application metrics (Spring Boot Actuator)
- Infrastructure metrics (Kubernetes, PostgreSQL)
- Custom business metrics (PLC connections, AI predictions)

### Dashboards

- **VirtPLC Overview**: System-wide health and performance
- **Factory Details**: Per-factory metrics and KPIs
- **Infrastructure**: Kubernetes cluster monitoring

## CI/CD

### GitHub Actions Workflows

1. **CI/CD Pipeline** (`ci-cd.yaml`):
   - Automated testing for all components
   - Docker image building and pushing
   - Staging deployment on develop branch
   - Production deployment on main branch

2. **Factory Provisioning** (`factory-provisioning.yaml`):

   - On-demand factory deployment
   - Automated namespace and secret creation
   - Health verification and documentation updates

### Deployment Process

1. Code changes trigger CI pipeline
2. Tests run for all modified components
3. Docker images are built and pushed to GHCR
4. Global components are updated in staging/production
5. Factory deployments are handled separately via provisioning workflow

## Scaling

### Horizontal Pod Autoscaling

- Backend services scale based on CPU/memory usage
- AI service scales based on request load
- Frontend scales based on traffic patterns

### Database Scaling

- PostgreSQL storage can be increased per factory
- Read replicas can be added for high-traffic factories
- Connection pooling managed by HikariCP

## Backup and Recovery

### Database Backups

- Automated backups using PostgreSQL backup tools
- Cross-region replication for disaster recovery
- Point-in-time recovery capabilities

### Application Backups

- Helm release snapshots for quick rollback
- Configuration backups in Git
- Container image immutability

## Troubleshooting

### Common Issues

1. **Factory deployment fails**
   - Check namespace creation
   - Verify storage class availability
   - Review Helm release status

2. **Ingress routing issues**
   - Verify ingress class configuration
   - Check TLS certificate status
   - Review NGINX ingress logs

3. **Monitoring not collecting metrics**
   - Check service discovery configuration
   - Verify network policies allow monitoring traffic
   - Review Prometheus target status

### Logs and Debugging

```bash
# View factory logs
kubectl logs -n virtplc-factory-a -l app.kubernetes.io/component=backend

# Check Helm release status
helm status factory-a -n virtplc-factory-a

# Debug ingress issues
kubectl describe ingress virtplc-ingress -n virtplc-system
```

## Contributing

1. Update Helm charts in `infra/helm/`
2. Test changes locally with `helm template`
3. Update documentation in this README
4. Create pull request with changes

## Support

For issues and questions:

- Check the troubleshooting section above
- Review GitHub Issues for known problems
- Contact the DevOps team for cluster-specific issues
