# Quick Reference: Kubernetes Multi-Tenant Commands

## 🚀 Initial Setup (One-Time)

```bash
# Automated setup (installs minikube, builds images, deploys infrastructure + 2 tenants)
./setup-k8s.sh
```

## 🏢 Tenant Management

### Provision New Tenant
```bash
cd kubernetes
./provision-tenant.sh <tenant_id> "Company Name" <domain>

# Examples:
./provision-tenant.sh acme123 "ACME Corporation" acme.virtplc.local
./provision-tenant.sh mfg789 "Manufacturing Co" mfg.virtplc.local
```

### List All Tenants
```bash
kubectl get namespaces | grep virtplc-
```

### Delete Tenant
```bash
kubectl delete namespace virtplc-<tenant_id>

# Example:
kubectl delete namespace virtplc-acme123
```

## 📊 Monitoring & Debugging

### View All Pods
```bash
# All namespaces
kubectl get pods --all-namespaces | grep virtplc

# Infrastructure
kubectl get pods -n virtplc-system

# Specific tenant
kubectl get pods -n virtplc-acme123
```

### View Logs
```bash
# Backend logs
kubectl logs -n virtplc-acme123 deployment/virtplc-backend --tail=50 --follow

# AI service logs
kubectl logs -n virtplc-acme123 deployment/virtplc-ai-service --tail=50 --follow

# PostgreSQL logs
kubectl logs -n virtplc-system statefulset/virtplc-postgres --tail=100
```

### Shell into Pod
```bash
# Get pod name
POD=$(kubectl get pod -n virtplc-acme123 -l app=virtplc-backend -o jsonpath='{.items[0].metadata.name}')

# Open shell
kubectl exec -it -n virtplc-acme123 $POD -- /bin/bash
```

### Check Service Health
```bash
# ACME tenant
curl http://api.acme.virtplc.local/actuator/health

# TechCorp tenant
curl http://api.techcorp.virtplc.local/actuator/health
```

### View Events (Troubleshooting)
```bash
# Recent events for a tenant
kubectl get events -n virtplc-acme123 --sort-by='.lastTimestamp'

# All events
kubectl get events --all-namespaces --sort-by='.lastTimestamp' | head -20
```

## 🧪 Testing

### Test Multi-Tenant Isolation
```bash
cd kubernetes
./test-isolation.sh
```

### Manual Network Isolation Test
```bash
# Get ACME pod name
ACME_POD=$(kubectl get pod -n virtplc-acme123 -l app=virtplc-backend -o jsonpath='{.items[0].metadata.name}')

# Try to access TechCorp backend (should fail)
kubectl exec -n virtplc-acme123 $ACME_POD -- curl -s --max-time 5 http://virtplc-backend.virtplc-tech456.svc.cluster.local:8080/actuator/health
```

### Database Isolation Test
```bash
# Get PostgreSQL pod
POSTGRES_POD=$(kubectl get pod -n virtplc-system -l app=postgres -o jsonpath='{.items[0].metadata.name}')

# List tenant schemas
kubectl exec -n virtplc-system $POSTGRES_POD -- psql -U virtplc -d virtplc -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'tenant_%';"

# View ACME data (isolated)
kubectl exec -n virtplc-system $POSTGRES_POD -- psql -U virtplc -d virtplc -c "SELECT COUNT(*) FROM tenant_acme123.plc_data;"

# View TechCorp data (isolated)
kubectl exec -n virtplc-system $POSTGRES_POD -- psql -U virtplc -d virtplc -c "SELECT COUNT(*) FROM tenant_tech456.plc_data;"
```

## 🔧 Cluster Management

### View Cluster Info
```bash
kubectl cluster-info
kubectl get nodes
kubectl top nodes
```

### View Resource Usage
```bash
# Per-pod resource usage
kubectl top pods -n virtplc-acme123
kubectl top pods -n virtplc-tech456

# Overall cluster usage
kubectl top nodes
```

### Open Kubernetes Dashboard
```bash
minikube dashboard
```

### Get Minikube IP
```bash
minikube ip
```

### Restart Minikube
```bash
minikube stop
minikube start
```

## 🔄 Updates & Rebuilds

### Rebuild Single Service
```bash
# Switch to minikube docker
eval $(minikube docker-env)

# Rebuild backend
cd backend && docker build -t virtplc/backend:latest .

# Restart deployment
kubectl rollout restart deployment/virtplc-backend -n virtplc-acme123
```

### Rebuild All Services
```bash
eval $(minikube docker-env)
cd backend && docker build -t virtplc/backend:latest . && cd ..
cd frontend && docker build -t virtplc/frontend:latest . && cd ..
cd ai-service && docker build -t virtplc/ai-service:latest . && cd ..

# Restart all tenant deployments
kubectl rollout restart deployment -n virtplc-acme123
kubectl rollout restart deployment -n virtplc-tech456
```

### Update Infrastructure
```bash
cd kubernetes

# Update shared services
kubectl apply -f infrastructure.yaml
kubectl apply -f services.yaml

# Restart infrastructure pods
kubectl rollout restart deployment -n virtplc-system
kubectl rollout restart statefulset -n virtplc-system
```

## 🌐 Ingress & DNS

### List Ingress Rules
```bash
kubectl get ingress --all-namespaces
kubectl describe ingress -n virtplc-acme123
```

### Update /etc/hosts
```bash
MINIKUBE_IP=$(minikube ip)
sudo nano /etc/hosts

# Add lines:
# <minikube-ip> acme.virtplc.local
# <minikube-ip> api.acme.virtplc.local
```

### Test DNS Resolution
```bash
nslookup acme.virtplc.local
curl -v http://acme.virtplc.local
```

## 🗑️ Cleanup

### Delete Single Tenant
```bash
kubectl delete namespace virtplc-acme123
```

### Delete All Tenants (Keep Infrastructure)
```bash
kubectl delete namespace -l tenant-isolation=true
```

### Delete Everything
```bash
minikube delete
```

### Reset /etc/hosts
```bash
sudo nano /etc/hosts
# Remove lines containing "virtplc.local"
```

## 🐛 Common Issues

### Pods Stuck in "Pending"
```bash
# Check pod details
kubectl describe pod <pod-name> -n <namespace>

# Check node resources
kubectl top nodes
```

### ImagePullBackOff Error
```bash
# Ensure images built in minikube docker
eval $(minikube docker-env)
docker images | grep virtplc

# Rebuild if needed
cd backend && docker build -t virtplc/backend:latest .

# Set imagePullPolicy to Never
kubectl patch deployment virtplc-backend -n virtplc-acme123 -p '{"spec":{"template":{"spec":{"containers":[{"name":"backend","imagePullPolicy":"Never"}]}}}}'
```

### Ingress Not Working
```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress rules
kubectl describe ingress -n virtplc-acme123

# Verify DNS
curl -v http://api.acme.virtplc.local
```

### Database Connection Failed
```bash
# Check PostgreSQL pod
kubectl logs -n virtplc-system statefulset/virtplc-postgres

# Test connection from backend pod
POD=$(kubectl get pod -n virtplc-acme123 -l app=virtplc-backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n virtplc-acme123 $POD -- nc -zv virtplc-postgres.virtplc-system.svc.cluster.local 5432
```

## 📚 Documentation

- Full setup guide: `docs/deployment/KUBERNETES_QUICKSTART.md`
- Architecture overview: `kubernetes/README.md`
- Provisioning script: `kubernetes/provision-tenant.sh`
- Isolation testing: `kubernetes/test-isolation.sh`

## 🎯 Quick Test Flow

```bash
# 1. Setup cluster (one-time)
./setup-k8s.sh

# 2. Verify infrastructure
kubectl get pods -n virtplc-system

# 3. Verify tenants
kubectl get pods -n virtplc-acme123
kubectl get pods -n virtplc-tech456

# 4. Test isolation
cd kubernetes && ./test-isolation.sh

# 5. Access frontends
curl http://api.acme.virtplc.local/actuator/health
curl http://api.techcorp.virtplc.local/actuator/health

# 6. Open in browser
xdg-open http://acme.virtplc.local
xdg-open http://techcorp.virtplc.local
```
