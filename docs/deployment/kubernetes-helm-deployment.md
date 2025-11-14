# VirtPLC Kubernetes Deployment with Helm

This comprehensive guide provides step-by-step instructions for deploying VirtPLC to a production Kubernetes cluster using Helm charts. This deployment option is recommended for enterprise-scale deployments with high availability, scalability, and multi-tenant requirements.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Kubernetes Cluster Setup](#kubernetes-cluster-setup)
4. [Helm Installation](#helm-installation)
5. [VirtPLC Helm Deployment](#virtplc-helm-deployment)
6. [Configuration](#configuration)
7. [Monitoring and Observability](#monitoring-and-observability)
8. [Scaling and Maintenance](#scaling-and-maintenance)
9. [Troubleshooting](#troubleshooting)
10. [Backup and Recovery](#backup-and-recovery)

## Prerequisites

### Hardware Requirements

**Minimum Cluster Specifications:**

- **Control Plane Nodes**: 3 nodes × (2 vCPU, 4GB RAM, 50GB SSD)
- **Worker Nodes**: 3-5 nodes × (4-8 vCPU, 16-32GB RAM, 200GB SSD)
- **Load Balancer**: 1 node × (2 vCPU, 4GB RAM, 50GB SSD)
- **Storage**: 500GB+ SSD for persistent volumes

**Recommended for Production:**

- **Control Plane Nodes**: 3 nodes × (4 vCPU, 8GB RAM, 100GB SSD)
- **Worker Nodes**: 5+ nodes × (8-16 vCPU, 32-64GB RAM, 500GB SSD)
- **Network**: 10Gbps internal, 1Gbps external

### Software Requirements

- **Operating System**: Ubuntu 22.04 LTS or RHEL 8+
- **Kubernetes**: v1.27+
- **Helm**: v3.12+
- **Container Runtime**: containerd 1.7+
- **Network Plugin**: Calico or Cilium
- **Ingress Controller**: NGINX Ingress Controller
- **Certificate Manager**: cert-manager
- **Storage Class**: Support for SSD-backed persistent volumes

### Network Requirements

**Required Ports:**

- **API Server (6443)**: Kubernetes API access
- **etcd (2379-2380)**: etcd client/server communication
- **Kubelet (10250)**: Kubelet API
- **NodePort Range (30000-32767)**: NodePort services
- **HTTP/HTTPS (80/443)**: Ingress traffic

**DNS Requirements:**

- Wildcard DNS record for your domain (e.g., `*.yourdomain.com`)
- API subdomain (e.g., `api.yourdomain.com`)
- Separate domains for each tenant if using multi-tenant setup

## Infrastructure Setup

### 1. Provision Servers

Choose your infrastructure provider:

**AWS EKS:**

```bash
# Create EKS cluster
eksctl create cluster \
  --name virtplc-prod \
  --version 1.27 \
  --region us-east-1 \
  --nodegroup-name workers \
  --node-type t3.large \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 10 \
  --managed
```

**Azure AKS:**

```bash
# Create AKS cluster
az aks create \
  --resource-group virtplc-rg \
  --name virtplc-prod \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --node-vm-size Standard_D4s_v3
```

**Google Cloud GKE:**

```bash
# Create GKE cluster
gcloud container clusters create virtplc-prod \
  --num-nodes=3 \
  --machine-type=e2-standard-4 \
  --zone=us-central1-a \
  --enable-autoscaling \
  --min-nodes=3 \
  --max-nodes=10
```

**On-Premise/Bare Metal:**

Use tools like:

- **kubeadm** for manual cluster setup
- **k3s** for lightweight clusters
- **Rancher** for enterprise management

### 2. Configure Storage

**AWS EBS:**

```bash
# Create storage class for SSD volumes
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: virtplc-ssd
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
reclaimPolicy: Retain
EOF
```

**Azure Disk:**

```bash
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: virtplc-ssd
provisioner: disk.csi.azure.com
parameters:
  skuName: Premium_LRS
reclaimPolicy: Retain
EOF
```

**NFS (On-Premise):**

```bash
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: virtplc-nfs
provisioner: nfs.csi.k8s.io
parameters:
  server: nfs-server.example.com
  share: /virtplc-data
reclaimPolicy: Retain
EOF
```

## Kubernetes Cluster Setup

### 1. Install Kubernetes

**Using kubeadm (On-Premise):**

```bash
# On all nodes - Install dependencies
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl

# Install containerd
sudo apt install -y containerd
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
sudo systemctl restart containerd

# Install kubelet, kubeadm, kubectl
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.27/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.27/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# Initialize control plane (first master node)
sudo kubeadm init --pod-network-cidr=192.168.0.0/16

# Set up kubectl for regular user
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install Calico network plugin
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

# Join worker nodes (run on each worker)
sudo kubeadm join <control-plane-ip>:6443 --token <token> --discovery-token-ca-cert-hash <hash>
```

### 2. Install Ingress Controller

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Wait for ingress controller to be ready
kubectl wait --for=condition=available --timeout=300s deployment/ingress-nginx-controller -n ingress-nginx
```

### 3. Install cert-manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.3/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --for=condition=available --timeout=300s deployment/cert-manager -n cert-manager
kubectl wait --for=condition=available --timeout=300s deployment/cert-manager-cainjector -n cert-manager
kubectl wait --for=condition=available --timeout=300s deployment/cert-manager-webhook -n cert-manager
```

### 4. Configure Cluster Autoscaling (Optional)

**AWS:**

```bash
# Install Cluster Autoscaler
kubectl apply -f https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml
```

**Azure:**

```bash
# AKS has built-in autoscaling
az aks update \
  --resource-group virtplc-rg \
  --name virtplc-prod \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 10
```

## Helm Installation

### 1. Install Helm

```bash
# Download and install Helm
curl https://get.helm.sh/helm-v3.12.3-linux-amd64.tar.gz -o helm.tar.gz
tar -zxvf helm.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm

# Verify installation
helm version
```

### 2. Add Required Helm Repositories

```bash
# Add Bitnami repository (for PostgreSQL, Redis)
helm repo add bitnami https://charts.bitnami.com/bitnami

# Add Ollama Helm repository
helm repo add ollama https://otwld.github.io/ollama-helm/

# Add Prometheus community repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# Update repositories
helm repo update
```

### 3. Create Namespace

```bash
kubectl create namespace virtplc-system
kubectl create namespace virtplc-tenants
```

## VirtPLC Helm Deployment

### 1. Clone Repository

```bash
git clone https://github.com/your-org/virtplc.git
cd virtplc
```

### 2. Create Secrets

```bash
# Generate secrets
export POSTGRES_PASSWORD=$(openssl rand -base64 32)
export REDIS_PASSWORD=$(openssl rand -base64 32)
export JWT_SECRET=$(openssl rand -base64 32)

# Create secrets
kubectl create secret generic virtplc-secrets \
  --from-literal=postgres-password=$POSTGRES_PASSWORD \
  --from-literal=redis-password=$REDIS_PASSWORD \
  --from-literal=jwt-secret=$JWT_SECRET \
  -n virtplc-system
```

### 3. Deploy PostgreSQL (TimescaleDB)

```bash
# Create PostgreSQL values file
cat > postgres-values.yaml << EOF
architecture: standalone
auth:
  postgresPassword: $POSTGRES_PASSWORD
  username: virtplc
  password: $POSTGRES_PASSWORD
  database: virtplc_prod

primary:
  persistence:
    enabled: true
    size: 100Gi
    storageClass: virtplc-ssd

metrics:
  enabled: true
  serviceMonitor:
    enabled: true
EOF

# Install PostgreSQL
helm install virtplc-postgres bitnami/postgresql \
  -f postgres-values.yaml \
  -n virtplc-system

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=available --timeout=600s deployment/virtplc-postgres-postgresql -n virtplc-system
```

### 4. Deploy Redis

```bash
# Create Redis values file
cat > redis-values.yaml << EOF
architecture: standalone
auth:
  password: $REDIS_PASSWORD

master:
  persistence:
    enabled: true
    size: 10Gi
    storageClass: virtplc-ssd

metrics:
  enabled: true
  serviceMonitor:
    enabled: true
EOF

# Install Redis
helm install virtplc-redis bitnami/redis \
  -f redis-values.yaml \
  -n virtplc-system

# Wait for Redis to be ready
kubectl wait --for=condition=available --timeout=300s deployment/virtplc-redis-master -n virtplc-system
```

### 5. Deploy Ollama

```bash
# Create Ollama values file
cat > ollama-values.yaml << EOF
ollama:
  gpu:
    enabled: false  # Set to true if GPU nodes available

persistence:
  enabled: true
  size: 100Gi
  storageClass: virtplc-ssd

service:
  type: ClusterIP
  port: 11434

resources:
  requests:
    memory: "4Gi"
    cpu: "2"
  limits:
    memory: "8Gi"
    cpu: "4"
EOF

# Install Ollama
helm install ollama ollama/ollama \
  -f ollama-values.yaml \
  -n virtplc-system

# Wait for Ollama to be ready
kubectl wait --for=condition=available --timeout=300s deployment/ollama -n virtplc-system
```

### 6. Deploy VirtPLC Shared Infrastructure

```bash
# Apply shared Kubernetes manifests
kubectl apply -f kubernetes/namespaces.yaml
kubectl apply -f kubernetes/configmaps.yaml
kubectl apply -f kubernetes/network-policies.yaml

# Deploy shared services
kubectl apply -f kubernetes/infrastructure.yaml
```

### 7. Deploy Monitoring Stack (Optional but Recommended)

```bash
# Install Prometheus
helm install prometheus prometheus-community/prometheus \
  -n virtplc-system

# Install Grafana
helm install grafana bitnami/grafana \
  -n virtplc-system
```

## Configuration

### 1. Domain Configuration

```bash
# Create ClusterIssuer for Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 2. Ingress Configuration

```bash
# Create ingress for shared services
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: virtplc-shared-ingress
  namespace: virtplc-system
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: virtplc-api-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: virtplc-backend
            port:
              number: 8080
EOF
```

### 3. Environment Variables

Create a ConfigMap for shared configuration:

```bash
kubectl create configmap virtplc-config \
  --from-literal=domain=yourdomain.com \
  --from-literal=environment=production \
  --from-literal=log-level=INFO \
  -n virtplc-system
```

## Tenant Provisioning

### 1. Provision First Tenant

```bash
# Make provision script executable
chmod +x kubernetes/provision-tenant.sh

# Provision tenant
./kubernetes/provision-tenant.sh tenant001 "Your Company Name" yourdomain.com
```

### 2. Verify Deployment

```bash
# Check pod status
kubectl get pods -n virtplc-tenant001

# Check services
kubectl get services -n virtplc-tenant001

# Check ingress
kubectl get ingress -n virtplc-tenant001
```

### 3. Access Application

- **Frontend**: `https://yourdomain.com`
- **API**: `https://api.yourdomain.com`
- **Health Check**: `https://api.yourdomain.com/actuator/health`

## Monitoring and Observability

### 1. Access Grafana

```bash
# Get Grafana admin password
kubectl get secret grafana-admin --namespace virtplc-system -o jsonpath="{.data.GF_SECURITY_ADMIN_PASSWORD}" | base64 --decode

# Port forward Grafana
kubectl port-forward svc/grafana 3000:80 -n virtplc-system

# Access at http://localhost:3000
```

### 2. Access Prometheus

```bash
# Port forward Prometheus
kubectl port-forward svc/prometheus-server 9090:80 -n virtplc-system

# Access at http://localhost:9090
```

### 3. Application Metrics

VirtPLC exposes metrics at:

- Backend: `/actuator/prometheus`
- AI Service: `/metrics`
- Frontend: Custom metrics via backend proxy

## Scaling and Maintenance

### 1. Horizontal Pod Autoscaling

```bash
# Create HPA for backend
kubectl autoscale deployment virtplc-backend \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n virtplc-tenant001
```

### 2. Vertical Scaling

```bash
# Update resource requests/limits
kubectl set resources deployment virtplc-backend \
  --requests=cpu=500m,memory=1Gi \
  --limits=cpu=2000m,memory=4Gi \
  -n virtplc-tenant001
```

### 3. Database Maintenance

```bash
# Scale down application before maintenance
kubectl scale deployment virtplc-backend --replicas=0 -n virtplc-tenant001

# Perform database maintenance (backups, vacuum, etc.)

# Scale back up
kubectl scale deployment virtplc-backend --replicas=3 -n virtplc-tenant001
```

## Troubleshooting

### 1. Common Issues

**Pods not starting:**

```bash
# Check pod events
kubectl describe pod <pod-name> -n <namespace>

# Check logs
kubectl logs <pod-name> -n <namespace>
```

**Ingress not working:**

```bash
# Check ingress status
kubectl describe ingress <ingress-name> -n <namespace>

# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

**Database connection issues:**

```bash
# Test database connectivity
kubectl exec -it virtplc-postgres-postgresql-0 -n virtplc-system -- psql -U virtplc -d virtplc_prod
```

### 2. Debug Commands

```bash
# Get cluster status
kubectl cluster-info

# Check node status
kubectl get nodes

# Check all resources
kubectl get all -n virtplc-system
kubectl get all -n virtplc-tenant001

# Check events
kubectl get events -n virtplc-system --sort-by=.metadata.creationTimestamp

# Check persistent volumes
kubectl get pv,pvc -n virtplc-system
```

### 3. Log Aggregation

```bash
# View logs from all pods in namespace
kubectl logs -l app=virtplc-backend -n virtplc-tenant001 --tail=100

# Follow logs in real-time
kubectl logs -f deployment/virtplc-backend -n virtplc-tenant001
```

## Backup and Recovery

### 1. Database Backup

```bash
# Create backup job
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: virtplc-db-backup
  namespace: virtplc-system
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h virtplc-postgres-postgresql -U virtplc virtplc_prod > /backup/backup.sql
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: virtplc-secrets
                  key: postgres-password
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: virtplc-backup-pvc
          restartPolicy: OnFailure
EOF
```

### 2. Configuration Backup

```bash
# Backup all Kubernetes resources
kubectl get all,configmap,secret,ingress,pvc -n virtplc-system -o yaml > virtplc-system-backup.yaml
kubectl get all,configmap,secret,ingress,pvc -n virtplc-tenant001 -o yaml > tenant001-backup.yaml
```

### 3. Disaster Recovery

```bash
# Restore from backup
kubectl apply -f virtplc-system-backup.yaml
kubectl apply -f tenant001-backup.yaml

# Restore database
kubectl exec -it virtplc-postgres-postgresql-0 -n virtplc-system -- psql -U virtplc -d virtplc_prod < backup.sql
```

## Security Considerations

### 1. Network Security

```bash
# Apply network policies
kubectl apply -f kubernetes/network-policies.yaml

# Enable pod security standards
kubectl label namespace virtplc-system pod-security.kubernetes.io/enforce=baseline
kubectl label namespace virtplc-tenants pod-security.kubernetes.io/enforce=baseline
```

### 2. Secret Management

```bash
# Use external secret management (Vault, AWS Secrets Manager, etc.)
# Rotate secrets regularly
kubectl create job --from=cronjob/secret-rotation secret-rotation-manual -n virtplc-system
```

### 3. RBAC Configuration

```bash
# Create service accounts with minimal permissions
kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: virtplc-backend-sa
  namespace: virtplc-tenant001
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: virtplc-backend-role
  namespace: virtplc-tenant001
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
EOF
```

## Performance Optimization

### 1. Resource Optimization

```bash
# Set appropriate resource limits
kubectl apply -f - <<EOF
apiVersion: v1
kind: LimitRange
metadata:
  name: virtplc-limits
  namespace: virtplc-tenant001
spec:
  limits:
  - default:
      cpu: 1000m
      memory: 2Gi
    defaultRequest:
      cpu: 100m
      memory: 256Mi
    type: Container
EOF
```

### 2. Database Optimization

```bash
# Enable TimescaleDB compression
kubectl exec -it virtplc-postgres-postgresql-0 -n virtplc-system -- psql -U virtplc -d virtplc_prod -c "
ALTER TABLE sensor_data SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'device_id',
  timescaledb.compress_orderby = 'timestamp DESC'
);
"
```

### 3. Caching Strategy

```bash
# Configure Redis for application caching
# Set appropriate cache TTL values in application configuration
```

## Conclusion

This deployment guide provides a production-ready Kubernetes setup for VirtPLC. The multi-tenant architecture ensures isolation between tenants while sharing infrastructure costs. Regular monitoring, backups, and security updates are essential for maintaining a reliable production environment.

For additional support or customizations, refer to the VirtPLC documentation or contact the development team.
