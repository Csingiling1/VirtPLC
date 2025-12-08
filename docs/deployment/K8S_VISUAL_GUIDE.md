# Kubernetes Multi-Tenant Deployment - Visual Workflow

## 🎬 Complete Deployment Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT DECISION TREE                     │
└─────────────────────────────────────────────────────────────────┘

                        "I want to deploy VirtPLC"
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │   How many tenants/      │
                    │   customers do you have?  │
                    └───────────┬───────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
        ┌───────────────┐              ┌──────────────┐
        │  1-3 tenants  │              │  5+ tenants  │
        │  or testing   │              │  or SaaS     │
        └───────┬───────┘              └──────┬───────┘
                │                             │
                ▼                             ▼
    ┌────────────────────┐        ┌────────────────────┐
    │  DOCKER COMPOSE    │        │   KUBERNETES       │
    │  ./deploy.sh dev   │        │  ./setup-k8s.sh    │
    └────────────────────┘        └────────────────────┘
```

## 🚀 Kubernetes Setup Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                     ./setup-k8s.sh WORKFLOW                       │
└──────────────────────────────────────────────────────────────────┘

Step 1: Prerequisites Check
┌─────────────────────────────┐
│ ✓ Check kubectl installed   │
│ ✓ Check/install minikube    │
│ ✓ Check Docker available    │
└──────────────┬──────────────┘
               │
               ▼
Step 2: Start Kubernetes Cluster
┌─────────────────────────────┐
│ $ minikube start            │
│   --cpus=4                  │
│   --memory=8192             │
│   --disk-size=40g           │
│                             │
│ $ minikube addons enable    │
│   ingress                   │
└──────────────┬──────────────┘
               │
               ▼
Step 3: Build Docker Images
┌─────────────────────────────┐
│ $ eval $(minikube docker-env)│
│                             │
│ Building (in parallel):     │
│  ├─ backend                 │
│  ├─ frontend                │
│  ├─ ai-service              │
│  ├─ collector               │
│  └─ simulator               │
└──────────────┬──────────────┘
               │
               ▼
Step 4: Deploy Shared Infrastructure
┌─────────────────────────────┐
│ virtplc-system namespace:   │
│  ├─ PostgreSQL/TimescaleDB  │
│  ├─ Redis Cache             │
│  ├─ Ollama AI Service       │
│  ├─ MQTT Broker             │
│  └─ Node-RED                │
│                             │
│ $ kubectl apply -f          │
│   - namespaces.yaml         │
│   - secrets.yaml            │
│   - configmaps.yaml         │
│   - infrastructure.yaml     │
│   - services.yaml           │
└──────────────┬──────────────┘
               │
               ▼
Step 5: Provision Demo Tenants
┌─────────────────────────────┐
│ Tenant 1: ACME Corporation  │
│  Domain: acme.virtplc.local │
│  Namespace: virtplc-acme123 │
│                             │
│ Tenant 2: TechCorp          │
│  Domain: techcorp.virtplc.  │
│           local             │
│  Namespace: virtplc-tech456 │
│                             │
│ Each tenant gets:           │
│  ├─ Backend (2 replicas)    │
│  ├─ Frontend (1 replica)    │
│  ├─ AI Service (1 replica)  │
│  ├─ Network Policies        │
│  ├─ Ingress Rules           │
│  └─ DB Schema               │
└──────────────┬──────────────┘
               │
               ▼
Step 6: Configure DNS
┌─────────────────────────────┐
│ Add to /etc/hosts:          │
│                             │
│ <minikube-ip> acme.virtplc. │
│               local         │
│ <minikube-ip> api.acme.     │
│               virtplc.local │
│ <minikube-ip> techcorp.     │
│               virtplc.local │
│ <minikube-ip> api.techcorp. │
│               virtplc.local │
└──────────────┬──────────────┘
               │
               ▼
Step 7: Success! ✅
┌─────────────────────────────┐
│ Cluster Ready               │
│                             │
│ Access:                     │
│  • http://acme.virtplc.local│
│  • http://techcorp.virtplc. │
│    local                    │
│                             │
│ Commands:                   │
│  • kubectl get pods -A      │
│  • minikube dashboard       │
│  • ./test-isolation.sh      │
└─────────────────────────────┘
```

## 🏗️ Infrastructure Layer View

```
┌────────────────────────────────────────────────────────────────┐
│                      KUBERNETES CLUSTER                         │
│                        (minikube)                               │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               INGRESS CONTROLLER (nginx)                  │  │
│  │  Routes:                                                  │  │
│  │   acme.virtplc.local → virtplc-acme123/frontend          │  │
│  │   api.acme.virtplc.local → virtplc-acme123/backend       │  │
│  │   techcorp.virtplc.local → virtplc-tech456/frontend      │  │
│  │   api.techcorp.virtplc.local → virtplc-tech456/backend   │  │
│  └─────────────────────────┬────────────────────────────────┘  │
│                            │                                    │
│  ┌─────────────────────────┴────────────────────────────────┐  │
│  │                     NAMESPACES                            │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────┐     │  │
│  │  │  virtplc-system (Shared Infrastructure)         │     │  │
│  │  │                                                  │     │  │
│  │  │  ┌──────────────┐  ┌──────────────┐            │     │  │
│  │  │  │  PostgreSQL  │  │    Redis     │            │     │  │
│  │  │  │  TimescaleDB │  │    Cache     │            │     │  │
│  │  │  │   (1 pod)    │  │   (1 pod)    │            │     │  │
│  │  │  └──────────────┘  └──────────────┘            │     │  │
│  │  │                                                  │     │  │
│  │  │  ┌──────────────┐  ┌──────────────┐            │     │  │
│  │  │  │    Ollama    │  │     MQTT     │            │     │  │
│  │  │  │  AI Models   │  │    Broker    │            │     │  │
│  │  │  │   (1 pod)    │  │   (1 pod)    │            │     │  │
│  │  │  └──────────────┘  └──────────────┘            │     │  │
│  │  │                                                  │     │  │
│  │  │  ┌──────────────┐                               │     │  │
│  │  │  │   Node-RED   │                               │     │  │
│  │  │  │  Enrichment  │                               │     │  │
│  │  │  │   (1 pod)    │                               │     │  │
│  │  │  └──────────────┘                               │     │  │
│  │  └─────────────────────────────────────────────────┘     │  │
│  │                            │                              │  │
│  │            ┌───────────────┼───────────────┐             │  │
│  │            │               │               │             │  │
│  │  ┌─────────▼─────────┐    │    ┌─────────▼─────────┐   │  │
│  │  │ virtplc-acme123   │    │    │ virtplc-tech456   │   │  │
│  │  │ (ACME Corp)       │    │    │ (TechCorp)        │   │  │
│  │  │                   │    │    │                   │   │  │
│  │  │ ┌───────────────┐ │    │    │ ┌───────────────┐ │   │  │
│  │  │ │ Backend       │ │    │    │ │ Backend       │ │   │  │
│  │  │ │ (2 pods)      │ │    │    │ │ (2 pods)      │ │   │  │
│  │  │ └───────────────┘ │    │    │ └───────────────┘ │   │  │
│  │  │                   │    │    │                   │   │  │
│  │  │ ┌───────────────┐ │    │    │ ┌───────────────┐ │   │  │
│  │  │ │ Frontend      │ │    │    │ │ Frontend      │ │   │  │
│  │  │ │ (1 pod)       │ │    │    │ │ (1 pod)       │ │   │  │
│  │  │ └───────────────┘ │    │    │ └───────────────┘ │   │  │
│  │  │                   │    │    │                   │   │  │
│  │  │ ┌───────────────┐ │    │    │ ┌───────────────┐ │   │  │
│  │  │ │ AI Service    │ │    │    │ │ AI Service    │ │   │  │
│  │  │ │ (1 pod)       │ │    │    │ │ (1 pod)       │ │   │  │
│  │  │ └───────────────┘ │    │    │ └───────────────┘ │   │  │
│  │  │                   │    │    │                   │   │  │
│  │  │ [Network Policy]  │    │    │ [Network Policy]  │   │  │
│  │  │ [DB Schema:       │    │    │ [DB Schema:       │   │  │
│  │  │  tenant_acme123]  │    │    │  tenant_tech456]  │   │  │
│  │  └───────────────────┘    │    └───────────────────┘   │  │
│  │                            │                            │  │
│  │                            ▼                            │  │
│  │                   Add more tenants with:               │  │
│  │              ./provision-tenant.sh <id>                │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## 🔄 Tenant Provisioning Flow

```
┌───────────────────────────────────────────────────────────────┐
│        ./provision-tenant.sh mfg789 "Mfg Co" mfg.local        │
└───────────────────────────────────────────────────────────────┘

Step 1: Create Namespace
┌──────────────────────────┐
│ kubectl create namespace │
│   virtplc-mfg789         │
│                          │
│ Add labels:              │
│  tenant-isolation=true   │
│  tenant-id=mfg789        │
└──────────┬───────────────┘
           │
           ▼
Step 2: Generate Secrets
┌──────────────────────────┐
│ Generate random:         │
│  • JWT_SECRET (32 bytes) │
│  • DB_PASSWORD (16 bytes)│
│                          │
│ Create K8s Secret:       │
│  tenant-secrets-mfg789   │
└──────────┬───────────────┘
           │
           ▼
Step 3: Create ConfigMap
┌──────────────────────────┐
│ tenant-config-mfg789:    │
│  • TENANT_ID: mfg789     │
│  • COMPANY: Mfg Co       │
│  • DB_HOST: postgres...  │
│  • REDIS_HOST: redis...  │
└──────────┬───────────────┘
           │
           ▼
Step 4: Create DB Schema
┌──────────────────────────┐
│ In PostgreSQL:           │
│  CREATE SCHEMA           │
│    tenant_mfg789;        │
│                          │
│  GRANT privileges to     │
│    tenant user           │
└──────────┬───────────────┘
           │
           ▼
Step 5: Deploy Services
┌──────────────────────────┐
│ Deploy from templates:   │
│  • Backend (2 replicas)  │
│  • Frontend (1 replica)  │
│  • AI Service (1 replica)│
│                          │
│ Each pod gets:           │
│  • Env vars from config  │
│  • Secrets mounted       │
│  • Resource limits       │
│  • Health checks         │
└──────────┬───────────────┘
           │
           ▼
Step 6: Configure Ingress
┌──────────────────────────┐
│ Create Ingress rules:    │
│                          │
│  mfg.local →             │
│    frontend-service      │
│                          │
│  api.mfg.local →         │
│    backend-service       │
└──────────┬───────────────┘
           │
           ▼
Step 7: Apply Network Policies
┌──────────────────────────┐
│ Create policies:         │
│                          │
│  • Deny cross-namespace  │
│  • Allow ingress access  │
│  • Allow shared infra    │
│  • Allow DNS resolution  │
└──────────┬───────────────┘
           │
           ▼
Step 8: Wait for Ready
┌──────────────────────────┐
│ kubectl wait             │
│   --for=condition=ready  │
│   pod -l app=backend     │
│   -n virtplc-mfg789      │
│                          │
│ Timeout: 300s            │
└──────────┬───────────────┘
           │
           ▼
✅ Tenant Provisioned!
┌──────────────────────────┐
│ Access URLs:             │
│  • http://mfg.local      │
│  • http://api.mfg.local  │
│                          │
│ Credentials saved in:    │
│  tenant-secrets-mfg789   │
│                          │
│ Time: ~30-60 seconds     │
└──────────────────────────┘
```

## 🧪 Testing Multi-Tenant Isolation

```
┌───────────────────────────────────────────────────────────────┐
│                  ./test-isolation.sh                           │
└───────────────────────────────────────────────────────────────┘

Test 1: Network Isolation
┌─────────────────────────────────────┐
│ From ACME pod, try to access:       │
│  techcorp-backend:8080              │
│                                     │
│ Expected: Connection timeout/refused│
│ Reason: Network policy blocks it    │
│                                     │
│ ✅ PASS: Cross-tenant blocked       │
└─────────────────────────────────────┘

Test 2: Database Isolation
┌─────────────────────────────────────┐
│ Query PostgreSQL for schemas:       │
│  • tenant_acme123 ✓                 │
│  • tenant_tech456 ✓                 │
│  • tenant_mfg789  ✓                 │
│                                     │
│ Each schema has own tables:         │
│  • plc_data                         │
│  • devices                          │
│  • factories                        │
│                                     │
│ ✅ PASS: Schemas isolated           │
└─────────────────────────────────────┘

Test 3: Secret Isolation
┌─────────────────────────────────────┐
│ Try to read TechCorp secret from    │
│ ACME namespace:                     │
│                                     │
│ $ kubectl get secret                │
│     tenant-secrets-tech456          │
│     -n virtplc-acme123              │
│                                     │
│ Expected: Error (not found)         │
│                                     │
│ ✅ PASS: Secrets isolated           │
└─────────────────────────────────────┘

Test 4: Ingress Routing
┌─────────────────────────────────────┐
│ Test domain routing:                │
│                                     │
│ $ curl acme.local                   │
│   → Returns ACME frontend ✓         │
│                                     │
│ $ curl techcorp.local               │
│   → Returns TechCorp frontend ✓     │
│                                     │
│ $ curl api.acme.local/health        │
│   → Returns ACME backend ✓          │
│                                     │
│ ✅ PASS: Routing works correctly    │
└─────────────────────────────────────┘

Test 5: Resource Limits
┌─────────────────────────────────────┐
│ Check pod resources:                │
│                                     │
│ $ kubectl top pods -n virtplc-acme123│
│   backend-xxx  250m  512Mi          │
│   frontend-xxx 100m  256Mi          │
│                                     │
│ Limits enforced:                    │
│  Backend: 500m CPU, 1Gi RAM         │
│  Frontend: 250m CPU, 512Mi RAM      │
│                                     │
│ ✅ PASS: Limits configured          │
└─────────────────────────────────────┘

Summary
┌─────────────────────────────────────┐
│ All 5 tests passed! ✅              │
│                                     │
│ Multi-tenant isolation verified:    │
│  ✓ Network policies work            │
│  ✓ Database schemas separate        │
│  ✓ Secrets scoped properly          │
│  ✓ Ingress routes correctly         │
│  ✓ Resource limits enforced         │
└─────────────────────────────────────┘
```

## 📊 Resource Usage Breakdown

```
┌────────────────────────────────────────────────────────────────┐
│                    RESOURCE ALLOCATION                          │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Shared Infrastructure (virtplc-system)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ PostgreSQL:     1 GB RAM,  500m CPU                      │  │
│  │ Redis:          512 MB RAM, 250m CPU                     │  │
│  │ Ollama:         2 GB RAM,   1000m CPU                    │  │
│  │ MQTT:           256 MB RAM, 100m CPU                     │  │
│  │ Node-RED:       512 MB RAM, 250m CPU                     │  │
│  │                                                          │  │
│  │ Total:          ~4.3 GB RAM, ~2.1 CPU                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Per Tenant (e.g., virtplc-acme123)                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Backend (2x):    2 GB RAM (1 GB each), 1000m CPU         │  │
│  │ Frontend (1x):   512 MB RAM, 250m CPU                    │  │
│  │ AI Service (1x): 512 MB RAM, 250m CPU                    │  │
│  │                                                          │  │
│  │ Total:          ~3 GB RAM, ~1.5 CPU                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Cluster with 3 Tenants                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Infrastructure:  4.3 GB RAM, 2.1 CPU                     │  │
│  │ Tenant 1:        3.0 GB RAM, 1.5 CPU                     │  │
│  │ Tenant 2:        3.0 GB RAM, 1.5 CPU                     │  │
│  │ Tenant 3:        3.0 GB RAM, 1.5 CPU                     │  │
│  │ K8s Overhead:    1.0 GB RAM, 0.5 CPU                     │  │
│  │                                                          │  │
│  │ Total:          ~14.3 GB RAM, ~7.1 CPU                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Recommended Node Size for 3 Tenants:                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • 16 GB RAM                                              │  │
│  │ • 8 CPU cores                                            │  │
│  │ • 100 GB disk                                            │  │
│  │                                                          │  │
│  │ Examples:                                                │  │
│  │  - Minikube: --memory=16384 --cpus=8                    │  │
│  │  - GKE: n1-standard-8                                    │  │
│  │  - AWS: t3.2xlarge                                       │  │
│  │  - Azure: Standard_D8s_v3                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

## 🎯 Success Timeline

```
Minute 0:  Run ./setup-k8s.sh
Minute 1:  ├─ Minikube starting...
Minute 2:  ├─ Cluster ready, building images...
Minute 5:  ├─ Images built, deploying infrastructure...
Minute 7:  ├─ PostgreSQL ready ✓
Minute 8:  ├─ Redis ready ✓
Minute 9:  ├─ Ollama ready ✓
Minute 10: ├─ Provisioning ACME tenant...
Minute 11: ├─ ACME backend ready ✓
Minute 12: ├─ Provisioning TechCorp tenant...
Minute 13: ├─ TechCorp backend ready ✓
Minute 14: ├─ Configuring DNS...
Minute 15: └─ ✅ COMPLETE!

           Open browser: http://acme.virtplc.local
```

---

**Ready to start? Run: `./setup-k8s.sh` 🚀**
