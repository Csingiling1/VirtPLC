# VirtPLC - Industrial IoT & Control System

An Accenture Challenge - Full-Stack IIoT Platform with Multi-Tenant Architecture

## Overview

VirtPLC is a comprehensive Industrial IoT platform providing real-time PLC data collection, AI-powered analytics, and multi-tenant SaaS deployment capabilities. The system features an MQTT-based data pipeline with Node-RED enrichment, TimescaleDB for time-series storage, and Kubernetes-ready multi-tenant isolation.

**Key Capabilities:**
- 🏭 Real-time industrial data collection from PLCs and IoT devices
- 📊 AI-powered natural language queries and analytics
- 🔄 High-performance data pipeline with automatic enrichment
- 🏢 Multi-tenant SaaS architecture with complete isolation
- 📈 Advanced time-series data storage and analysis
- 🎨 Modern web-based HMI and dashboards

## Project Structure

```
VirtPLC/
├── ai-service/           # AI/ML service (FastAPI + Ollama)
│   ├── src/             # Python source code
│   ├── tests/           # Unit and integration tests
│   └── README.md        # AI service documentation
├── backend/             # REST API (Spring Boot)
│   ├── src/             # Java source code
│   └── README.md        # Backend API documentation
├── collector/           # MQTT to TimescaleDB ingestion (Go)
│   ├── main.go          # Main collector service
│   └── README.md        # Collector documentation
├── frontend/            # Web UI (React + TypeScript + Vite)
│   ├── src/             # React components and pages
│   └── README.md        # Frontend documentation
├── HMI/                 # Ignition HMI integration
│   └── README.md        # HMI setup guide
├── nodered/             # Data enrichment pipeline
│   ├── flows/           # Node-RED flow configurations
│   └── README.md        # Pipeline documentation
├── simulator/           # PLC/factory simulator
│   └── README.md        # Simulator documentation
├── nginx/               # Reverse proxy and API gateway
│   └── README.md        # NGINX configuration guide
├── monitoring/          # Observability stack (Prometheus, Grafana)
│   └── README.md        # Monitoring setup guide
├── kubernetes/          # K8s multi-tenant deployment
│   ├── namespaces.yaml  # Namespace configurations
│   ├── services.yaml    # Service definitions
│   └── README.md        # Kubernetes deployment guide
├── infra/               # Infrastructure as Code
│   ├── helm/            # Helm charts
│   └── k8s/             # Kubernetes manifests
├── docs/                # Comprehensive documentation
│   ├── deployment/      # Deployment guides
│   ├── testing/         # Testing documentation
│   └── README.md        # Documentation index
├── scripts/             # Utility and maintenance scripts
│   └── README.md        # Scripts documentation
└── docker-compose.yml   # Local development setup
```

## Quick Start

### Docker Compose (Development/Single-Tenant)
```bash
# Development mode with hot reload
./deploy.sh dev

# Production mode (single tenant)
./deploy.sh prod

# View logs
docker-compose logs -f

# Access services:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8080
# - AI Service: http://localhost:3001
# - Node-RED: http://localhost:1880
```

### Kubernetes (Multi-Tenant SaaS)
```bash
# Automated setup (builds images, deploys infrastructure, provisions 2 demo tenants)
./setup-k8s.sh

# Manually provision additional tenants
cd kubernetes
./provision-tenant.sh <tenant_id> "Company Name" <domain>

# Test multi-tenant isolation
./kubernetes/test-isolation.sh

# Access tenants:
# - Tenant 1: http://acme.virtplc.local
# - Tenant 2: http://techcorp.virtplc.local
```

See: **[K8S_GETTING_STARTED.md](K8S_GETTING_STARTED.md)** for full Kubernetes setup guide

## Architecture

### Data Pipeline
```
PLC Simulator → MQTT (plc/{device_id}) → Node-RED (Enrichment) 
    → Collector → TimescaleDB → AI Service (Natural Language Queries)
```

### Components
- **Simulator**: Python-based PLC/factory simulator with 35+ devices
- **MQTT Broker**: Eclipse Mosquitto 2.0 with authentication
- **Node-RED**: Data validation, enrichment, and routing
- **Collector**: Go service writing to TimescaleDB
- **TimescaleDB**: PostgreSQL + timescaledb extension for time-series data
- **Backend**: Spring Boot (Java) REST API
- **Frontend**: React + TypeScript + Vite
- **AI Service**: FastAPI + Ollama for natural language factory queries
- **Cleanup Service**: Automated data retention (deletes 25% every 2 months)

### Multi-Tenant Kubernetes Architecture
- **Shared Infrastructure**: PostgreSQL, Redis, Ollama, MQTT, Node-RED (virtplc-system namespace)
- **Isolated Tenants**: Each company gets separate namespace with backend, frontend, AI service
- **Network Policies**: Prevent cross-tenant communication
- **Database Schemas**: Separate schema per tenant (tenant_acme123, tenant_tech456)
- **Custom Domains**: Ingress routes traffic by domain (acme.virtplc.com, techcorp.virtplc.com)

## Features

### Core Platform
- ✅ Real-time PLC data collection (MQTT-based)
- ✅ Data enrichment and validation (Node-RED)
- ✅ Time-series storage with automatic compression (TimescaleDB)
- ✅ RESTful API for factory data access
- ✅ Interactive frontend dashboard
- ✅ Automated data cleanup (retention policies)

### AI Capabilities
- ✅ Natural language queries ("Show me average temperature for PLC001")
- ✅ Factory statistics and summaries
- ✅ Sensor value lookups by name
- ✅ Time-series analysis and aggregations
- ✅ Device search and filtering

### Multi-Tenant Features (Kubernetes)
- ✅ Isolated namespaces per tenant
- ✅ Network policy enforcement
- ✅ Separate database schemas
- ✅ Custom domain routing
- ✅ Resource quotas and limits
- ✅ Automated tenant provisioning
- ✅ Zero-downtime rolling updates

## Documentation

### Deployment
- **[K8S_GETTING_STARTED.md](K8S_GETTING_STARTED.md)** - Quick start for Kubernetes multi-tenant deployment
- **[docs/deployment/KUBERNETES_QUICKSTART.md](docs/deployment/KUBERNETES_QUICKSTART.md)** - Detailed K8s setup guide
- **[docs/deployment/K8S_COMMANDS.md](docs/deployment/K8S_COMMANDS.md)** - Kubernetes command reference
- **[docs/deployment/DEPLOYMENT_COMPARISON.md](docs/deployment/DEPLOYMENT_COMPARISON.md)** - Docker Compose vs Kubernetes comparison
- **[DEPLOYMENT_PROFILES.md](DEPLOYMENT_PROFILES.md)** - Docker Compose profiles (dev, stage2, prod)
- **[README_DOCKER.md](README_DOCKER.md)** - Docker Compose architecture

### Services & Features
- **[AI_SERVICE_UPDATES.md](AI_SERVICE_UPDATES.md)** - AI service capabilities and API
- **[PIPELINE_STATUS.md](PIPELINE_STATUS.md)** - Data pipeline verification
- **[docs/ORCHESTRATION.md](docs/ORCHESTRATION.md)** - System orchestration guide
- **[docs/Setup.md](docs/Setup.md)** - Initial setup instructions
- **[docs/Integration.md](docs/Integration.md)** - Service integration guide

### Kubernetes
- **[kubernetes/README.md](kubernetes/README.md)** - Architecture overview
- **[kubernetes/provision-tenant.sh](kubernetes/provision-tenant.sh)** - Tenant provisioning script
- **[kubernetes/test-isolation.sh](kubernetes/test-isolation.sh)** - Multi-tenant isolation tests
