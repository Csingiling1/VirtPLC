#!/bin/bash

# VirtPLC Kubernetes Multi-Tenant Setup Script
# This script automates the setup of a local Kubernetes cluster with minikube
# and deploys the VirtPLC multi-tenant infrastructure

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🚀 VirtPLC Kubernetes Multi-Tenant Setup"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo -e "${YELLOW}⚠️  Minikube not found. Installing...${NC}"
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    sudo install minikube-linux-amd64 /usr/local/bin/minikube
    rm minikube-linux-amd64
    echo -e "${GREEN}✅ Minikube installed${NC}"
else
    echo -e "${GREEN}✅ Minikube already installed${NC}"
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found. Please install kubectl first.${NC}"
    exit 1
else
    echo -e "${GREEN}✅ kubectl found${NC}"
fi

# Check if cluster is already running
if minikube status &> /dev/null; then
    echo -e "${YELLOW}⚠️  Minikube cluster already running${NC}"
    read -p "Delete and recreate cluster? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Deleting existing cluster..."
        minikube delete
    else
        echo "Using existing cluster"
        SKIP_CLUSTER_START=true
    fi
fi

# Start minikube cluster
if [ "$SKIP_CLUSTER_START" != true ]; then
    echo ""
    echo "🎬 Starting Minikube cluster..."
    echo "   CPUs: 4, Memory: 8GB, Disk: 40GB"
    minikube start --cpus=4 --memory=8192 --disk-size=40g --driver=docker

    echo ""
    echo "🔌 Enabling ingress addon..."
    minikube addons enable ingress

    echo ""
    echo "⏳ Waiting for ingress controller to be ready..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s
fi

echo ""
echo "📦 Building Docker images in minikube..."
eval $(minikube docker-env)

cd "$PROJECT_ROOT"

echo "   Building backend..."
(cd backend && docker build -t virtplc/backend:latest . -q) &
BACKEND_PID=$!

echo "   Building frontend..."
(cd frontend && docker build -t virtplc/frontend:latest . -q) &
FRONTEND_PID=$!

echo "   Building AI service..."
(cd ai-service && docker build -t virtplc/ai-service:latest . -q) &
AI_PID=$!

echo "   Building collector..."
(cd collector && docker build -t virtplc/collector:latest . -q) &
COLLECTOR_PID=$!

echo "   Building simulator..."
(cd simulator && docker build -t virtplc/simulator:latest . -q) &
SIMULATOR_PID=$!

# Wait for all builds
wait $BACKEND_PID $FRONTEND_PID $AI_PID $COLLECTOR_PID $SIMULATOR_PID

echo -e "${GREEN}✅ All images built${NC}"
echo ""
docker images | grep virtplc

echo ""
echo "🏗️  Deploying shared infrastructure..."
cd "$PROJECT_ROOT/kubernetes"

# Create namespaces
echo "   Creating namespaces..."
kubectl apply -f namespaces.yaml

# Create secrets and configmaps
echo "   Creating secrets and configmaps..."
kubectl apply -f secrets.yaml 2>/dev/null || echo "   (Secrets may already exist)"
kubectl apply -f configmaps.yaml

# Deploy infrastructure
echo "   Deploying PostgreSQL, Redis, Ollama..."
kubectl apply -f infrastructure.yaml

# Deploy services
echo "   Deploying MQTT, Node-RED, TimescaleDB..."
kubectl apply -f services.yaml

echo ""
echo "⏳ Waiting for infrastructure to be ready (this may take 3-5 minutes)..."

# Wait for PostgreSQL
echo "   Waiting for PostgreSQL..."
kubectl wait --for=condition=ready pod -l app=postgres -n virtplc-system --timeout=300s || true

# Wait for Redis
echo "   Waiting for Redis..."
kubectl wait --for=condition=ready pod -l app=redis -n virtplc-system --timeout=300s || true

# Wait for Ollama
echo "   Waiting for Ollama..."
kubectl wait --for=condition=ready pod -l app=ollama -n virtplc-system --timeout=300s || true

echo ""
echo -e "${GREEN}✅ Infrastructure deployed successfully${NC}"
echo ""
kubectl get pods -n virtplc-system

echo ""
echo "🏢 Provisioning demo tenants..."

# Make provision script executable
chmod +x provision-tenant.sh

# Provision first tenant
echo ""
echo "   Tenant 1: ACME Corporation"
./provision-tenant.sh acme123 "ACME Corporation" acme.virtplc.local || echo "   (May already exist)"

# Provision second tenant
echo ""
echo "   Tenant 2: TechCorp Industries"
./provision-tenant.sh tech456 "TechCorp Industries" techcorp.virtplc.local || echo "   (May already exist)"

echo ""
echo "🌐 Configuring local DNS..."
MINIKUBE_IP=$(minikube ip)
echo "   Minikube IP: $MINIKUBE_IP"

# Check if entries already exist
if grep -q "virtplc.local" /etc/hosts; then
    echo -e "${YELLOW}   ⚠️  DNS entries already exist in /etc/hosts${NC}"
else
    echo "   Adding DNS entries to /etc/hosts (requires sudo)..."
    sudo tee -a /etc/hosts > /dev/null <<EOF

# VirtPLC Multi-Tenant K8s (added by setup script)
$MINIKUBE_IP acme.virtplc.local
$MINIKUBE_IP api.acme.virtplc.local
$MINIKUBE_IP techcorp.virtplc.local
$MINIKUBE_IP api.techcorp.virtplc.local
EOF
    echo -e "${GREEN}   ✅ DNS entries added${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Cluster Status:"
kubectl get nodes
echo ""
kubectl get namespaces | grep virtplc
echo ""

echo "🌐 Access URLs:"
echo "   ACME Corporation:"
echo "      Frontend: http://acme.virtplc.local"
echo "      API:      http://api.acme.virtplc.local/actuator/health"
echo ""
echo "   TechCorp Industries:"
echo "      Frontend: http://techcorp.virtplc.local"
echo "      API:      http://api.techcorp.virtplc.local/actuator/health"
echo ""

echo "📝 Useful Commands:"
echo "   View all pods:          kubectl get pods --all-namespaces"
echo "   View ACME pods:         kubectl get pods -n virtplc-acme123"
echo "   View TechCorp pods:     kubectl get pods -n virtplc-tech456"
echo "   View logs:              kubectl logs -n virtplc-acme123 deployment/virtplc-backend"
echo "   Open dashboard:         minikube dashboard"
echo "   Get cluster IP:         minikube ip"
echo ""

echo "🧪 Test Multi-Tenant Isolation:"
echo "   Network isolation test: ./kubernetes/test-isolation.sh"
echo ""

echo "🧹 Cleanup:"
echo "   Delete tenant:          kubectl delete namespace virtplc-acme123"
echo "   Delete cluster:         minikube delete"
echo ""

echo -e "${GREEN}Ready to use! Open http://acme.virtplc.local in your browser.${NC}"
