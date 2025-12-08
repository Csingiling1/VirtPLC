# Kubernetes Multi-Tenant Deployment - Quick Start Guide

This guide walks you through setting up and testing the VirtPLC multi-tenant Kubernetes infrastructure on your local machine.

## Prerequisites Check

✅ kubectl installed: `/usr/bin/kubectl`  
❌ Local K8s cluster needed (minikube/kind)

## Option 1: Local Testing with Minikube (Recommended)

### Step 1: Install Minikube

```bash
# Download and install minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify installation
minikube version
```

### Step 2: Start Minikube Cluster

```bash
# Start with sufficient resources for multi-tenant setup
minikube start --cpus=4 --memory=8192 --disk-size=40g --driver=docker

# Enable ingress addon (required for tenant routing)
minikube addons enable ingress

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

### Step 3: Build and Load Docker Images

Since minikube uses its own Docker daemon, you need to build images inside minikube:

```bash
# Point your shell to minikube's docker daemon
eval $(minikube docker-env)

# Build all service images
cd /home/deginandor/Documents/Programming/VirtPLC

# Backend
cd backend && docker build -t virtplc/backend:latest . && cd ..

# Frontend
cd frontend && docker build -t virtplc/frontend:latest . && cd ..

# AI Service
cd ai-service && docker build -t virtplc/ai-service:latest . && cd ..

# Collector
cd collector && docker build -t virtplc/collector:latest . && cd ..

# Simulator
cd simulator && docker build -t virtplc/simulator:latest . && cd ..

# Verify images are available
docker images | grep virtplc
```

### Step 4: Deploy Shared Infrastructure

```bash
cd kubernetes

# Create namespaces
kubectl apply -f namespaces.yaml

# Create shared secrets and configmaps
kubectl apply -f secrets.yaml
kubectl apply -f configmaps.yaml

# Deploy shared infrastructure (PostgreSQL, Redis, Ollama)
kubectl apply -f infrastructure.yaml

# Deploy shared services (MQTT, Node-RED, TimescaleDB)
kubectl apply -f services.yaml

# Wait for infrastructure to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n virtplc-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n virtplc-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=ollama -n virtplc-system --timeout=300s

# Check infrastructure status
kubectl get pods -n virtplc-system
```

### Step 5: Provision Your First Tenant

```bash
# Make provisioning script executable
chmod +x provision-tenant.sh

# Provision tenant "acme123" for ACME Corporation
./provision-tenant.sh acme123 "ACME Corporation" acme.virtplc.local

# The script will:
# 1. Create namespace virtplc-acme123
# 2. Generate secrets (JWT, DB password)
# 3. Deploy backend, frontend, AI service
# 4. Configure network policies for isolation
# 5. Set up ingress routes

# Check tenant deployment
kubectl get pods -n virtplc-acme123
kubectl get ingress -n virtplc-acme123
```

### Step 6: Provision Additional Tenants (Test Isolation)

```bash
# Provision second tenant
./provision-tenant.sh tech456 "TechCorp Industries" techcorp.virtplc.local

# Provision third tenant
./provision-tenant.sh mfg789 "Manufacturing Co" mfg.virtplc.local

# Verify all tenant namespaces
kubectl get namespaces | grep virtplc
kubectl get pods --all-namespaces | grep virtplc
```

### Step 7: Configure Local DNS (Access Tenants)

Since you're using local domains, add them to `/etc/hosts`:

```bash
# Get minikube IP
MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"

# Add tenant domains to /etc/hosts
sudo tee -a /etc/hosts <<EOF

# VirtPLC Multi-Tenant K8s
$MINIKUBE_IP acme.virtplc.local
$MINIKUBE_IP api.acme.virtplc.local
$MINIKUBE_IP techcorp.virtplc.local
$MINIKUBE_IP api.techcorp.virtplc.local
$MINIKUBE_IP mfg.virtplc.local
$MINIKUBE_IP api.mfg.virtplc.local
EOF
```

### Step 8: Test Tenant Access

```bash
# Test ACME tenant frontend
curl http://acme.virtplc.local

# Test ACME tenant API health
curl http://api.acme.virtplc.local/actuator/health

# Test TechCorp tenant (separate instance)
curl http://api.techcorp.virtplc.local/actuator/health

# Open in browser
xdg-open http://acme.virtplc.local
xdg-open http://techcorp.virtplc.local
```

### Step 9: Verify Multi-Tenant Isolation

#### Test 1: Network Isolation (Pods can't talk across tenants)

```bash
# Try to access TechCorp backend from ACME pod (should fail)
ACME_POD=$(kubectl get pod -n virtplc-acme123 -l app=virtplc-backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n virtplc-acme123 $ACME_POD -- curl -s --max-time 5 http://virtplc-backend.virtplc-tech456.svc.cluster.local:8080/actuator/health || echo "✅ Network isolation working - cross-tenant access denied"
```

#### Test 2: Database Isolation (Separate schemas)

```bash
# Get PostgreSQL pod
POSTGRES_POD=$(kubectl get pod -n virtplc-system -l app=postgres -o jsonpath='{.items[0].metadata.name}')

# Check ACME schema exists
kubectl exec -n virtplc-system $POSTGRES_POD -- psql -U virtplc -d virtplc -c "\dn" | grep tenant_acme123

# Check TechCorp schema exists
kubectl exec -n virtplc-system $POSTGRES_POD -- psql -U virtplc -d virtplc -c "\dn" | grep tenant_tech456

# Verify tenants can only see their own data
kubectl exec -n virtplc-system $POSTGRES_POD -- psql -U virtplc -d virtplc -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'tenant_%';"
```

#### Test 3: Resource Quotas (Prevent tenant resource hogging)

```bash
# Check resource limits per tenant
kubectl describe namespace virtplc-acme123 | grep -A 10 "Resource Quotas"
kubectl top pods -n virtplc-acme123
kubectl top pods -n virtplc-tech456
```

### Step 10: Inspect Logs and Monitoring

```bash
# View ACME backend logs
kubectl logs -n virtplc-acme123 deployment/virtplc-backend --tail=50 --follow

# View TechCorp AI service logs
kubectl logs -n virtplc-tech456 deployment/virtplc-ai-service --tail=50 --follow

# View shared infrastructure logs
kubectl logs -n virtplc-system deployment/virtplc-postgres --tail=50
kubectl logs -n virtplc-system deployment/ollama-service --tail=50

# Get all events for troubleshooting
kubectl get events -n virtplc-acme123 --sort-by='.lastTimestamp'
```

## Option 2: Local Testing with Kind (Alternative)

If you prefer `kind` over `minikube`:

```bash
# Install kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Create cluster with ingress support
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF

# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for ingress to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s

# Load images into kind cluster
kind load docker-image virtplc/backend:latest
kind load docker-image virtplc/frontend:latest
kind load docker-image virtplc/ai-service:latest

# Continue with Step 4 above (Deploy Shared Infrastructure)
```

## Option 3: Cloud Deployment (Production-Ready)

### Google Kubernetes Engine (GKE)

```bash
# Create GKE cluster
gcloud container clusters create virtplc-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-4 \
  --enable-autorepair \
  --enable-autoupgrade

# Get credentials
gcloud container clusters get-credentials virtplc-cluster --zone us-central1-a

# Install NGINX Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Install cert-manager (for SSL/TLS)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Continue with Step 4 (Deploy Shared Infrastructure)
```

### Amazon EKS

```bash
# Create EKS cluster
eksctl create cluster \
  --name virtplc-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.large \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 5 \
  --managed

# Install AWS Load Balancer Controller
# (Follow AWS documentation for ALB controller setup)

# Continue with Step 4 (Deploy Shared Infrastructure)
```

## Troubleshooting

### Issue: Pods stuck in "Pending" state

```bash
# Check pod events
kubectl describe pod <pod-name> -n <namespace>

# Check if insufficient resources
kubectl top nodes
kubectl describe node minikube
```

### Issue: Ingress not routing traffic

```bash
# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Verify ingress rules
kubectl get ingress --all-namespaces
kubectl describe ingress -n virtplc-acme123
```

### Issue: Database connection failures

```bash
# Check PostgreSQL pod
kubectl logs -n virtplc-system statefulset/virtplc-postgres --tail=100

# Test connection from backend pod
kubectl exec -n virtplc-acme123 deployment/virtplc-backend -- curl -v telnet://virtplc-postgres.virtplc-system.svc.cluster.local:5432
```

### Issue: Images not found (ImagePullBackOff)

```bash
# If using minikube, ensure you built images in minikube's Docker
eval $(minikube docker-env)
docker images | grep virtplc

# Set imagePullPolicy to Never for local images
kubectl patch deployment virtplc-backend -n virtplc-acme123 -p '{"spec":{"template":{"spec":{"containers":[{"name":"backend","imagePullPolicy":"Never"}]}}}}'
```

## Cleanup

### Remove a single tenant

```bash
kubectl delete namespace virtplc-acme123
```

### Remove all tenants but keep infrastructure

```bash
kubectl delete namespace -l tenant-isolation=true
```

### Destroy entire cluster

```bash
# Minikube
minikube delete

# Kind
kind delete cluster

# GKE
gcloud container clusters delete virtplc-cluster --zone us-central1-a

# EKS
eksctl delete cluster --name virtplc-cluster --region us-east-1
```

## Next Steps

1. **Add Monitoring**: Deploy Prometheus + Grafana for metrics
2. **Enable SSL/TLS**: Configure cert-manager with Let's Encrypt
3. **Add GitOps**: Use ArgoCD or Flux for automated deployments
4. **Backup Strategy**: Set up Velero for cluster backups
5. **CI/CD Pipeline**: Automate tenant provisioning with GitHub Actions
6. **Resource Quotas**: Add per-tenant CPU/memory limits
7. **Horizontal Pod Autoscaling**: Scale based on load

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    Ingress Controller                       │
│              (Routes traffic by domain)                      │
└────────┬────────────────────┬────────────────────┬──────────┘
         │                    │                    │
         v                    v                    v
┌────────────────┐   ┌────────────────┐   ┌────────────────┐
│ virtplc-acme123│   │ virtplc-tech456│   │ virtplc-mfg789 │
│  (Namespace)   │   │  (Namespace)   │   │  (Namespace)   │
├────────────────┤   ├────────────────┤   ├────────────────┤
│ • Backend (2x) │   │ • Backend (2x) │   │ • Backend (2x) │
│ • Frontend (1x)│   │ • Frontend (1x)│   │ • Frontend (1x)│
│ • AI Svc (1x)  │   │ • AI Svc (1x)  │   │ • AI Svc (1x)  │
│ • Network      │   │ • Network      │   │ • Network      │
│   Policies     │   │   Policies     │   │   Policies     │
└────────┬───────┘   └────────┬───────┘   └────────┬───────┘
         │                    │                    │
         └────────────────────┴────────────────────┘
                              |
                              v
         ┌────────────────────────────────────────┐
         │      virtplc-system (Namespace)        │
         ├────────────────────────────────────────┤
         │ • PostgreSQL (TimescaleDB)             │
         │ • Redis Cache                          │
         │ • Ollama AI Models                     │
         │ • MQTT Broker                          │
         │ • Node-RED Flows                       │
         └────────────────────────────────────────┘
```

**Key Features:**
- **Isolation**: Network policies prevent cross-tenant communication
- **Shared Resources**: All tenants share PostgreSQL/Redis/Ollama (cost-efficient)
- **Separate Schemas**: Each tenant has isolated database schema
- **Custom Domains**: Each tenant gets unique domain routing
- **Auto-Scaling**: Deployments can scale based on load
- **Health Checks**: Automatic pod restarts on failures
