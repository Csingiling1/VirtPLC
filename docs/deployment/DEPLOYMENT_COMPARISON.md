# VirtPLC Deployment Options: Docker Compose vs Kubernetes

## Quick Decision Matrix

| Scenario | Recommended | Command |
|----------|------------|---------|
| Local development, single tenant | Docker Compose | `./deploy.sh dev` |
| Testing features, debugging | Docker Compose | `./deploy.sh dev` |
| Demo for one customer | Docker Compose | `./deploy.sh prod` |
| Multi-tenant SaaS platform | Kubernetes | `./setup-k8s.sh` |
| Need automatic scaling | Kubernetes | `./setup-k8s.sh` |
| Production with multiple customers | Kubernetes | Cloud deployment |

## Docker Compose Deployment

### ✅ Use When:
- Developing new features locally
- Testing changes quickly (fast iteration)
- Single-tenant deployment (one customer/instance)
- Running on a single server/VM
- Learning the system architecture
- Quick demos or POCs

### Pros:
- **Simple**: One command to start everything
- **Fast**: No cluster overhead, instant startup
- **Easy debugging**: Direct access to logs with `docker logs`
- **Lightweight**: Minimal resource usage
- **Portable**: Works on any machine with Docker

### Cons:
- ❌ No multi-tenant isolation (everyone shares same instance)
- ❌ Manual scaling (can't auto-scale based on load)
- ❌ Single point of failure (if server dies, everything stops)
- ❌ No automatic restarts across reboots (requires systemd/init scripts)
- ❌ Limited resource management per tenant

### Available Profiles:

#### Development (`dev`)
```bash
./deploy.sh dev
```
- Hot reload enabled
- Debug ports exposed
- Local volumes for code changes
- No authentication required
- **Use for**: Local development, testing

#### Stage 2 (`stage2`)
```bash
./deploy.sh stage2
```
- Full MQTT pipeline with Node-RED
- Includes AI service with Ollama
- All data flows through enrichment
- **Use for**: Testing complete pipeline, Node-RED debugging

#### Production (`prod`)
```bash
./deploy.sh prod
```
- Optimized images
- Health checks enabled
- Resource limits configured
- Authentication required
- **Use for**: Single-tenant production deployment

### Example: Local Development Workflow

```bash
# Start dev environment
./deploy.sh dev

# Make code changes (auto-reloads)
vim backend/src/main/java/com/virtplc/Controller.java

# View logs
docker-compose logs -f backend

# Restart single service
docker-compose restart backend

# Stop everything
docker-compose down
```

## Kubernetes Deployment

### ✅ Use When:
- Running SaaS platform (multiple customers/companies)
- Need tenant isolation (separate resources per customer)
- Require automatic scaling (handle load spikes)
- Need high availability (99.9%+ uptime)
- Want automatic failover (self-healing)
- Managing 5+ tenants

### Pros:
- **Multi-tenant**: Each customer gets isolated namespace
- **Auto-scaling**: Pods scale based on CPU/memory usage
- **High availability**: Automatic pod restarts and failover
- **Resource management**: CPU/memory limits per tenant
- **Network isolation**: Tenants can't access each other
- **Rolling updates**: Zero-downtime deployments
- **Production-grade**: Industry standard for cloud-native apps

### Cons:
- ⚠️ Complex setup (requires cluster, ingress, networking)
- ⚠️ Higher resource overhead (Kubernetes control plane)
- ⚠️ Steeper learning curve (kubectl, YAML manifests)
- ⚠️ Slower iteration (image rebuild + rollout)
- ⚠️ Requires more infrastructure (load balancers, persistent volumes)

### Deployment Options:

#### Local Testing (Minikube)
```bash
./setup-k8s.sh
```
- Single-node cluster on your laptop
- Test multi-tenant isolation
- Learn Kubernetes concepts
- **Use for**: K8s development, testing provisioning scripts

#### Cloud Production (GKE/EKS/AKS)
```bash
# See docs/deployment/KUBERNETES_QUICKSTART.md
gcloud container clusters create virtplc-cluster ...
```
- Multi-node cluster in cloud
- Auto-scaling, load balancing
- Persistent storage, backups
- **Use for**: Production SaaS platform

### Example: Multi-Tenant SaaS Workflow

```bash
# Setup cluster (one-time)
./setup-k8s.sh

# Customer signs up → provision tenant
cd kubernetes
./provision-tenant.sh acme123 "ACME Corp" acme.virtplc.com

# Customer accesses their instance
# → https://acme.virtplc.com

# Deploy backend update (zero downtime)
cd backend && docker build -t virtplc/backend:v2.0 .
kubectl set image deployment/virtplc-backend backend=virtplc/backend:v2.0 -n virtplc-acme123

# Scale up for high traffic
kubectl scale deployment/virtplc-backend --replicas=5 -n virtplc-acme123

# Customer churns → delete tenant
kubectl delete namespace virtplc-acme123
```

## Side-by-Side Comparison

| Feature | Docker Compose | Kubernetes |
|---------|---------------|------------|
| **Setup Time** | 2 minutes | 10 minutes |
| **Learning Curve** | Easy | Moderate |
| **Multi-Tenancy** | ❌ Shared instance | ✅ Isolated namespaces |
| **Auto-Scaling** | ❌ Manual | ✅ Horizontal Pod Autoscaler |
| **High Availability** | ❌ Single point of failure | ✅ Self-healing, replicas |
| **Resource Isolation** | ❌ Shared resources | ✅ Per-tenant limits |
| **Network Isolation** | ❌ Same network | ✅ Network policies |
| **Domain Routing** | ❌ Same domain | ✅ Custom domains per tenant |
| **Rolling Updates** | ❌ Downtime | ✅ Zero-downtime |
| **Cost (small scale)** | 💰 Low | 💰💰 Medium |
| **Cost (large scale)** | 💰💰💰 High (many VMs) | 💰💰 Medium (shared infra) |
| **Best For** | Dev, single-tenant | SaaS, multi-tenant |

## Hybrid Approach (Recommended)

### Development Phase
```bash
# Use Docker Compose for fast iteration
./deploy.sh dev

# Develop features
# Test locally
# Debug with logs
```

### Testing Phase
```bash
# Use Kubernetes for integration testing
./setup-k8s.sh

# Test multi-tenant isolation
cd kubernetes && ./test-isolation.sh

# Verify network policies work
# Test domain routing
```

### Production Phase
```bash
# Deploy to cloud Kubernetes
# Follow docs/deployment/KUBERNETES_QUICKSTART.md

# Provision production tenants
./provision-tenant.sh <id> "Company" <domain>
```

## Migration Path

### Step 1: Start with Docker Compose
```bash
# Initial development
./deploy.sh dev

# Single customer pilot
./deploy.sh prod
```

### Step 2: Test Kubernetes Locally
```bash
# Once you need multi-tenancy
./setup-k8s.sh

# Test with 2-3 tenants
./provision-tenant.sh tenant1 ...
./provision-tenant.sh tenant2 ...
```

### Step 3: Deploy to Cloud
```bash
# When ready for production
# Follow cloud setup in KUBERNETES_QUICKSTART.md
```

## Real-World Examples

### Scenario 1: Startup with 1-2 Customers
**Use Docker Compose** (`./deploy.sh prod`)
- Deploy on single VM ($20/month)
- Each customer gets separate VM
- Simple, cost-effective
- Easy to manage

### Scenario 2: Growing SaaS with 5-10 Customers
**Switch to Kubernetes** (`./setup-k8s.sh`)
- Deploy single K8s cluster
- Provision tenant per customer
- Shared infrastructure saves costs
- Easier to manage than 10 VMs

### Scenario 3: Enterprise SaaS with 100+ Customers
**Production Kubernetes** (Cloud deployment)
- Multi-node cluster
- Auto-scaling enabled
- Monitoring & alerting
- Automated provisioning
- CI/CD pipeline

## Resource Requirements

### Docker Compose (Single Instance)
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 40 GB
- **Cost**: ~$20-40/month (single VM)

### Kubernetes (10 Tenants)
- **CPU**: 8 cores (4 for control plane, 4 for workloads)
- **RAM**: 16 GB
- **Disk**: 100 GB
- **Cost**: ~$100-150/month (managed K8s)

### Cost Per Tenant

| Deployment | Fixed Cost | Per-Tenant Cost | 10 Tenants | 100 Tenants |
|------------|-----------|----------------|-----------|------------|
| Docker Compose (separate VMs) | $0 | $30/month | $300 | $3,000 |
| Kubernetes (shared cluster) | $50 | $5/month | $100 | $550 |

**Kubernetes becomes cost-effective at ~5+ tenants**

## When to Switch?

### Stick with Docker Compose if:
- You have 1-3 customers
- Single-tenant per deployment is acceptable
- Budget is very limited (<$100/month)
- Team has no Kubernetes experience

### Switch to Kubernetes when:
- You have 5+ customers (cost savings kick in)
- Customers need isolated environments
- You need automatic scaling
- Downtime is unacceptable (need HA)
- You're building a SaaS platform

## Summary

**For Development**: Always use Docker Compose (`./deploy.sh dev`)
- Fast, simple, easy debugging

**For Production**:
- **1-3 tenants**: Docker Compose (`./deploy.sh prod`)
- **5+ tenants**: Kubernetes (`./setup-k8s.sh`)

**For Learning**: Try both!
1. Start with `./deploy.sh dev` to understand the architecture
2. Then try `./setup-k8s.sh` to see multi-tenant isolation

---

## Quick Start Commands

### Docker Compose
```bash
# Development
./deploy.sh dev
docker-compose logs -f

# Production (single tenant)
./deploy.sh prod
```

### Kubernetes
```bash
# Local multi-tenant testing
./setup-k8s.sh
./kubernetes/test-isolation.sh

# Add tenant
cd kubernetes
./provision-tenant.sh acme123 "ACME" acme.local
```

Choose the right tool for the job! 🚀
