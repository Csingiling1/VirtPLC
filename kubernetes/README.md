# VirtPLC Kubernetes Deployment

This directory contains Kubernetes manifests for deploying VirtPLC in a multi-tenant architecture. Each company gets isolated resources while sharing the underlying infrastructure.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
├─────────────────────────────────────────────────────────────┤
│  virtplc-system (Shared Infrastructure)                    │
│  ├── PostgreSQL (TimescaleDB) - Shared database            │
│  ├── Redis - Shared cache                                   │
│  └── Ollama - Shared AI models                              │
├─────────────────────────────────────────────────────────────┤
│  virtplc-tenants (Per-Company Namespaces)                   │
│  ├── company-a (acme.virtplc.com)                          │
│  │   ├── Backend API (Spring Boot)                         │
│  │   ├── Frontend (React)                                   │
│  │   └── AI Service (FastAPI)                               │
│  ├── company-b (globex.virtplc.com)                        │
│  │   ├── Backend API (Spring Boot)                         │
│  │   ├── Frontend (React)                                   │
│  │   └── AI Service (FastAPI)                               │
│  └── ...                                                    │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

- **Multi-tenant Isolation**: Each company operates in its own Kubernetes namespace
- **Shared Infrastructure**: Common services (DB, Redis, AI models) are shared across tenants
- **Automatic Scaling**: Horizontal Pod Autoscaling based on resource usage
- **Network Security**: Network policies prevent cross-tenant communication
- **SSL/TLS**: Automatic certificate management with Let's Encrypt
- **High Availability**: Multi-replica deployments with rolling updates

## Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured
- Helm 3.x
- cert-manager for SSL certificates
- NGINX Ingress Controller
- Storage classes for persistent volumes

## Quick Start

### 1. Deploy Shared Infrastructure

```bash
# Deploy shared services
kubectl apply -f kubernetes/namespaces.yaml
kubectl apply -f kubernetes/configmaps.yaml
kubectl apply -f kubernetes/secrets.yaml
kubectl apply -f kubernetes/services.yaml
kubectl apply -f kubernetes/infrastructure.yaml

# Wait for infrastructure to be ready
kubectl wait --for=condition=available --timeout=600s deployment/virtplc-postgres -n virtplc-system
kubectl wait --for=condition=available --timeout=300s deployment/virtplc-redis -n virtplc-system
kubectl wait --for=condition=available --timeout=300s deployment/ollama-service -n virtplc-system
```

### 2. Provision a New Tenant

```bash
# Make the script executable
chmod +x kubernetes/provision-tenant.sh

# Provision a tenant
./kubernetes/provision-tenant.sh acme123 "ACME Corporation" acme.virtplc.com
```

This will:
- Create namespace `virtplc-acme123`
- Deploy backend, frontend, and AI service
- Configure ingress for `acme.virtplc.com` and `api.acme.virtplc.com`
- Set up network policies for isolation
- Generate unique secrets for the tenant

### 3. Access the Application

- **Frontend**: https://acme.virtplc.com
- **API**: https://api.acme.virtplc.com
- **Health Check**: https://api.acme.virtplc.com/actuator/health

## File Structure

```
kubernetes/
├── namespaces.yaml              # Namespace definitions
├── configmaps.yaml              # Shared configuration
├── secrets.yaml                 # Shared secrets
├── services.yaml                # Shared services and ingress
├── infrastructure.yaml          # StatefulSets and Deployments for shared services
├── tenant-deployment-template.yaml  # Template for tenant deployments
├── tenant-services-template.yaml    # Template for tenant services
├── network-policies.yaml        # Network isolation policies
├── provision-tenant.sh          # Automated tenant provisioning script
└── README.md                    # This file
```

## Configuration

### Environment Variables

Each tenant deployment uses the following environment variables:

**Backend Service:**
- `TENANT_ID`: Unique tenant identifier
- `DB_HOST`: PostgreSQL host
- `DB_PASSWORD`: Tenant-specific database password
- `JWT_SECRET`: Tenant-specific JWT signing key
- `REDIS_HOST`: Redis host
- `REDIS_PASSWORD`: Redis password

**AI Service:**
- `TENANT_ID`: Unique tenant identifier
- `OLLAMA_BASE_URL`: Ollama service URL

**Frontend:**
- `REACT_APP_API_URL`: Backend API URL
- `REACT_APP_TENANT_ID`: Tenant identifier

### Database Schema

Each tenant gets its own database schema within the shared PostgreSQL instance. The schema name follows the pattern `tenant_{TENANT_ID}`.

### Network Policies

- **Tenant Isolation**: Pods can only communicate within their namespace
- **Shared Services Access**: All tenants can access shared infrastructure
- **Ingress Control**: Only NGINX ingress can reach tenant services
- **Egress Control**: Limited outbound traffic for security

## Monitoring and Maintenance

### Health Checks

All services include readiness and liveness probes:
- Backend: `/actuator/health`
- AI Service: `/health`
- Frontend: HTTP 200 on `/`

### Logs

```bash
# View logs for a specific tenant
kubectl logs -n virtplc-acme123 deployment/virtplc-backend

# View logs for shared infrastructure
kubectl logs -n virtplc-system deployment/virtplc-postgres
```

### Scaling

```bash
# Scale backend deployment
kubectl scale deployment virtplc-backend -n virtplc-acme123 --replicas=3

# Scale AI service
kubectl scale deployment virtplc-ai-service -n virtplc-acme123 --replicas=2
```

### Updates

```bash
# Update tenant deployment
kubectl set image deployment/virtplc-backend backend=virtplc/backend:v2.1.0 -n virtplc-acme123

# Rolling update
kubectl rollout status deployment/virtplc-backend -n virtplc-acme123
```

## Security Considerations

1. **Secrets Management**: Use Kubernetes secrets or external secret managers
2. **Network Policies**: Regularly audit network policies
3. **RBAC**: Implement proper Role-Based Access Control
4. **Image Security**: Scan container images for vulnerabilities
5. **Certificate Rotation**: cert-manager handles automatic renewal

## Troubleshooting

### Common Issues

**Pods not starting:**
```bash
kubectl describe pod <pod-name> -n <tenant-namespace>
kubectl logs <pod-name> -n <tenant-namespace>
```

**Ingress not working:**
```bash
kubectl get ingress -n <tenant-namespace>
kubectl describe ingress <ingress-name> -n <tenant-namespace>
```

**Database connection issues:**
```bash
kubectl exec -it deployment/virtplc-postgres -n virtplc-system -- psql -U postgres -d virtplc
```

### Debug Commands

```bash
# Check all resources in a tenant namespace
kubectl get all -n virtplc-acme123

# Check network policies
kubectl get networkpolicies -n virtplc-acme123

# Check ingress
kubectl get ingress -n virtplc-acme123

# Check secrets
kubectl get secrets -n virtplc-acme123
```

## Backup and Recovery

### Database Backup

```bash
# Create database backup
kubectl exec -it deployment/virtplc-postgres -n virtplc-system -- pg_dump -U postgres virtplc > backup.sql

# Restore from backup
kubectl exec -it deployment/virtplc-postgres -n virtplc-system -- psql -U postgres virtplc < backup.sql
```

### Tenant Data Export

Each tenant's data can be exported using the backend API endpoints for backup purposes.

## Contributing

When making changes to the Kubernetes manifests:

1. Test changes in a development cluster first
2. Update this README if adding new features
3. Use template variables consistently
4. Follow Kubernetes best practices
5. Include resource limits and requests

## Support

For issues and questions:
- Check the troubleshooting section above
- Review Kubernetes logs
- Contact the DevOps team
- Create an issue in the project repository