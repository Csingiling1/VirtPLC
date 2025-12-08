# Kubernetes Multi-Tenant Deployment - Getting Started

## Overview

Your VirtPLC system now supports **multi-tenant Kubernetes deployment** where each company/customer gets:
- **Isolated namespace** with their own backend, frontend, and AI service
- **Separate database schema** for complete data isolation
- **Network policies** preventing cross-tenant communication
- **Custom domain routing** (e.g., acme.virtplc.com, techcorp.virtplc.com)
- **Shared infrastructure** (PostgreSQL, Redis, Ollama) for cost efficiency

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │      Ingress Controller             │
                    │   (Domain-based routing)            │
                    └──────┬──────────────┬───────────────┘
                           │              │
         ┌─────────────────┴───┐    ┌────┴──────────────────┐
         │  acme.virtplc.com   │    │ techcorp.virtplc.com  │
         │  (Tenant A)         │    │ (Tenant B)            │
         │                     │    │                       │
         │  • Backend (2 pods) │    │  • Backend (2 pods)   │
         │  • Frontend (1 pod) │    │  • Frontend (1 pod)   │
         │  • AI Service       │    │  • AI Service         │
         │  • Network Policies │    │  • Network Policies   │
         └──────────┬──────────┘    └────┬──────────────────┘
                    │                    │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │ Shared Resources   │
                    │                    │
                    │  • PostgreSQL/     │
                    │    TimescaleDB     │
                    │  • Redis Cache     │
                    │  • Ollama AI       │
                    │  • MQTT Broker     │
                    │  • Node-RED        │
                    └────────────────────┘
```

## Quick Start (5 Minutes)

### Option 1: Automated Setup ⚡ **RECOMMENDED**

```bash
cd /home/deginandor/Documents/Programming/VirtPLC
./setup-k8s.sh
```

This script will:
1. Install minikube (if needed)
2. Start a Kubernetes cluster
3. Build all Docker images
4. Deploy shared infrastructure (PostgreSQL, Redis, Ollama, MQTT, Node-RED)
5. Provision 2 demo tenants (ACME Corp, TechCorp)
6. Configure local DNS
7. Test the deployment

**Time:** ~5-10 minutes (depending on image build times)

### Option 2: Manual Setup 📚

Follow the detailed guide: `docs/deployment/KUBERNETES_QUICKSTART.md`

## Verify Deployment

After setup completes, run:

```bash
# Check cluster status
kubectl get nodes
kubectl get namespaces | grep virtplc

# Check infrastructure
kubectl get pods -n virtplc-system

# Check tenants
kubectl get pods -n virtplc-acme123
kubectl get pods -n virtplc-tech456

# Test isolation
cd kubernetes && ./test-isolation.sh

# Test API endpoints
curl http://api.acme.virtplc.local/actuator/health
curl http://api.techcorp.virtplc.local/actuator/health
```

## Access Tenants

Open in your browser:
- **ACME Corporation**: http://acme.virtplc.local
- **TechCorp Industries**: http://techcorp.virtplc.local

## Add More Tenants

```bash
cd kubernetes
./provision-tenant.sh <tenant_id> "Company Name" <domain>

# Example:
./provision-tenant.sh mfg789 "Manufacturing Co" mfg.virtplc.local
```

## Key Features Demonstrated

### ✅ Network Isolation
Pods in `virtplc-acme123` cannot communicate with pods in `virtplc-tech456`. Try:
```bash
./kubernetes/test-isolation.sh
```

### ✅ Database Isolation
Each tenant has a separate schema: `tenant_acme123`, `tenant_tech456`, etc.
```bash
POSTGRES_POD=$(kubectl get pod -n virtplc-system -l app=postgres -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n virtplc-system $POSTGRES_POD -- psql -U virtplc -d virtplc -c "\dn"
```

### ✅ Resource Limits
Each tenant pod has CPU/memory limits to prevent resource hogging:
```bash
kubectl top pods -n virtplc-acme123
kubectl top pods -n virtplc-tech456
```

### ✅ Custom Domain Routing
Ingress routes traffic based on domain:
```bash
kubectl get ingress --all-namespaces
```

## Common Tasks

### View Logs
```bash
# ACME backend logs
kubectl logs -n virtplc-acme123 deployment/virtplc-backend --tail=50 --follow

# Shared PostgreSQL logs
kubectl logs -n virtplc-system statefulset/virtplc-postgres --tail=100
```

### Update Services
```bash
# Rebuild backend image
eval $(minikube docker-env)
cd backend && docker build -t virtplc/backend:latest .

# Restart all tenants
kubectl rollout restart deployment/virtplc-backend -n virtplc-acme123
kubectl rollout restart deployment/virtplc-backend -n virtplc-tech456
```

### Delete Tenant
```bash
kubectl delete namespace virtplc-acme123
```

## Troubleshooting

### Pods not starting?
```bash
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace>
```

### Can't access domains?
```bash
# Check minikube IP
minikube ip

# Verify /etc/hosts has entries
grep virtplc.local /etc/hosts

# Test ingress
kubectl get ingress --all-namespaces
curl -v http://api.acme.virtplc.local
```

### Images not found?
```bash
# Ensure images built in minikube docker
eval $(minikube docker-env)
docker images | grep virtplc
```

## Documentation

- **Full Setup Guide**: `docs/deployment/KUBERNETES_QUICKSTART.md` - Complete step-by-step instructions
- **Command Reference**: `docs/deployment/K8S_COMMANDS.md` - Quick command cheat sheet
- **Architecture Details**: `kubernetes/README.md` - In-depth architecture documentation
- **Provisioning Script**: `kubernetes/provision-tenant.sh` - Tenant creation automation
- **Isolation Tests**: `kubernetes/test-isolation.sh` - Multi-tenant isolation verification

## What You've Built

1. **Multi-Tenant SaaS Platform**: Each customer gets isolated resources
2. **Cost-Efficient Architecture**: Shared infrastructure reduces overhead
3. **Automatic Scaling**: Kubernetes handles pod scaling and restarts
4. **Production-Ready**: Network policies, health checks, resource limits
5. **Easy Onboarding**: Provision new tenants in seconds with one command

## Next Steps

### For Local Development:
- Use Docker Compose: `./deploy.sh dev` (simpler, faster iteration)
- Switch to K8s when testing multi-tenancy or scaling

### For Production:
1. Deploy to cloud (GKE/EKS/AKS) - see KUBERNETES_QUICKSTART.md
2. Add SSL/TLS with cert-manager + Let's Encrypt
3. Set up monitoring (Prometheus + Grafana)
4. Configure backups (Velero)
5. Add CI/CD pipeline (GitHub Actions + ArgoCD)

## Questions?

- **How much does each tenant cost?** Shared infrastructure keeps costs low. Only backend/frontend/AI pods are duplicated per tenant.
- **How many tenants can I run?** Depends on cluster resources. Start with 3-5 per node, scale horizontally.
- **Can tenants access each other's data?** No. Network policies and database schemas enforce isolation.
- **How do I add custom domains?** Update ingress configuration and DNS records.
- **Can I test this without minikube?** Yes, use `kind` or a cloud provider (see KUBERNETES_QUICKSTART.md).

## Summary

You now have a **production-ready multi-tenant Kubernetes infrastructure** that:
- Isolates tenant resources with network policies and namespaces
- Shares infrastructure (PostgreSQL, Redis, Ollama) for efficiency
- Routes traffic by domain to the correct tenant
- Provisions new tenants in seconds
- Tests isolation automatically

**Get started now:** `./setup-k8s.sh` 🚀
