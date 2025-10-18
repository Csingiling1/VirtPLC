# VirtPLC - Virtual Factory PLC System

**Project:** VirtPLC | **Client:** Accenture Challenge | **Year:** 2025

Complete virtual factory monitoring and control system with Unreal Engine visualization, Ignition HMI, Spring Boot backend, React dashboard, and AI-powered predictive analytics.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         VirtPLC System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │ Unreal Engine│    │   Ignition   │    │React Frontend│    │
│  │  (UEBlender) │    │  HMI (Edge)  │    │   (Web UI)   │    │
│  │  Port: N/A   │    │  Port: 8088  │    │  Port: 3000  │    │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    │
│         │                   │                    │             │
│         │    OPC-UA         │       REST API     │             │
│         └───────────────────┼────────────────────┘             │
│                             │                                  │
│                    ┌────────▼────────┐                        │
│                    │  Spring Boot    │                        │
│                    │    Backend      │◄──────┐                │
│                    │  Port: 8080     │       │                │
│                    │  OPC-UA: 4840   │       │                │
│                    └────────┬────────┘       │                │
│                             │                │                │
│                     ┌───────▼───────┐  ┌─────▼──────┐        │
│                     │   TimeBase    │  │AI Service  │        │
│                     │   Database    │  │(Ollama)    │        │
│                     │  Port: 8011   │  │Port: 3001  │        │
│                     └───────────────┘  │  WS: 3002  │        │
│                                        └────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Components

### 1. **Unreal Engine + Blender** (`feature/UEBlender`)
Virtual 3D factory visualization with OPC-UA client integration.

- **Tech**: Unreal Engine 5.3+, Blender 4.0+, C++, open62541
- **Features**: Real-time 3D visualization, OPC-UA client, FBX asset pipeline
- **Location**: `UnrealProject/`, `BlenderAssets/`
- **Docs**: `Docs/Setup.md`, `Docs/OPC-UA-Schema.md`

### 2. **Ignition HMI** (`feature/HMI`)
Industrial HMI interface with OPC-UA integration and TimeBase historian.

- **Tech**: Ignition Edge, Perspective module, OPC-UA client, TimeBase
- **Features**: Live dashboards, tag configurations, historical trending
- **Location**: `IgnitionEdge/`, `TimeBaseDB/`
- **Docs**: `Docs/HMI-Design.md`, `Docs/Integration.md`
- **Port**: 8088 (web interface)

### 3. **Spring Boot Backend** (`feature/Web`)
REST API server with embedded OPC-UA server and JWT authentication.

- **Tech**: Spring Boot 3, Java 21, Eclipse Milo, JWT, Maven
- **Features**: OPC-UA server, REST API, JWT auth, TimeBase integration
- **Location**: `backend/`
- **Ports**: 8080 (REST), 4840 (OPC-UA)
- **Endpoints**: `/api/data/latest`, `/api/data/range`, `/auth/login`

### 4. **React Frontend** (`feature/Web`)
Web dashboard for monitoring and control.

- **Tech**: React 18, TypeScript, Vite, Recharts, Axios
- **Features**: Login, live metrics, HMI embed, real-time charts
- **Location**: `frontend/`
- **Port**: 3000
- **Routes**: `/login`, `/metrics`, `/hmi`

### 5. **AI Analysis Service** (`feature/AI`)
Predictive analytics and anomaly detection with Ollama integration.

- **Tech**: Node.js, Express, Ollama, WebSocket
- **Features**: AI analysis, predictive maintenance, anomaly detection, WebSocket streaming
- **Location**: `ai-service/`
- **Ports**: 3001 (REST), 3002 (WebSocket)
- **Endpoints**: `/api/analysis/analyze`, `/api/analysis/predict-maintenance`

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- (Optional) Ollama for AI features
- (Optional) Ignition Edge for HMI

### 1. Clone Repository

```bash
git clone https://github.com/Dedzsinator/VirtPLC.git
cd VirtPLC
git checkout develop
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start All Services

```bash
# Production mode
docker-compose up -d

# Development mode with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production mode with resource limits
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 4. Access Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **AI Service**: http://localhost:3001
- **Ignition HMI**: http://localhost:8088 (if installed separately)
- **OPC-UA**: opc.tcp://localhost:4840

### 5. Health Checks

```bash
# Backend
curl http://localhost:8080/api/data/health

# Frontend
curl http://localhost:3000

# AI Service
curl http://localhost:3001/health
```

## 📚 Branch Structure

```
release                 # Production-ready releases
  └── develop           # Main integration branch (Docker Compose here)
       ├── feature/UEBlender   # Unreal Engine + Blender
       ├── feature/HMI         # Ignition HMI configuration
       ├── feature/Web         # Backend + Frontend
       └── feature/AI          # AI analysis service
```

## 🔧 Development Workflow

### Working on a Feature Branch

```bash
# Checkout feature branch
git checkout feature/Web  # or UEBlender, HMI, AI

# Make changes
# ...

# Commit and push
git add .
git commit -m "feat(web): your changes"
git push origin feature/Web
```

### Integrating Changes to Develop

```bash
# Switch to develop
git checkout develop

# Merge feature branch
git merge feature/Web --no-ff

# Resolve conflicts if any
# ...

# Push to remote
git push origin develop
```

### Creating a Release

```bash
# From develop
git checkout develop
git pull origin develop

# Create release branch
git checkout -b release/v1.0.0

# Update version numbers, test everything
# ...

# Merge to release
git checkout release
git merge release/v1.0.0 --no-ff
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin release --tags

# Merge back to develop
git checkout develop
git merge release/v1.0.0 --no-ff
git push origin develop
```

## 🐳 Docker Commands

### Build Services

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
```

### Manage Services

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Restart service
docker-compose restart backend

# Scale service (if configured)
docker-compose up -d --scale ai-service=3
```

### Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## 🔐 Security

### JWT Authentication

Backend uses JWT for API authentication. Frontend automatically includes token in requests.

**Login:**
```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'
```

**Use Token:**
```bash
curl http://localhost:8080/api/data/latest \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Environment Variables

**Important**: Change these in production!

- `JWT_SECRET`: JWT signing key (min 256 bits)
- `TIMEBASE_PASSWORD`: TimeBase admin password
- Configure CORS origins in `application.yml`

## 📊 API Documentation

### Backend REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | Generate JWT token |
| `/auth/validate` | GET | Validate token |
| `/api/data/latest` | GET | Current sensor readings |
| `/api/data/range` | GET | Historical data |
| `/api/data/health` | GET | Health check |

### AI Service REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analysis/analyze` | POST | Analyze sensor data |
| `/api/analysis/predict-maintenance` | GET | Maintenance predictions |
| `/api/analysis/anomalies` | GET | Detect anomalies |
| `/api/analysis/status` | GET | Service status |
| `/health` | GET | Health check |

### WebSocket API

Connect to `ws://localhost:3002` for real-time AI analysis updates.

## 🔗 Integration Guide

### Connect Unreal Engine to OPC-UA

1. Build OPC-UA plugin (see `feature/UEBlender` docs)
2. Configure endpoint: `opc.tcp://localhost:4840`
3. Subscribe to nodes under `Factory/` namespace

### Connect Ignition Edge

1. Install Ignition Edge (see `feature/HMI` docs)
2. Configure OPC-UA connection to `opc.tcp://backend:4840`
3. Import tag definitions from `IgnitionEdge/tags/tag-definitions.json`
4. Deploy Perspective project

### Frontend API Integration

Frontend automatically connects to backend via Vite proxy in development, or Nginx reverse proxy in production.

## 🧪 Testing

### Backend Tests

```bash
cd backend
mvn test
```

### Frontend Tests

```bash
cd frontend
npm test
```

### AI Service Tests

```bash
cd ai-service
npm test
```

### Integration Tests

```bash
# Start all services
docker-compose up -d

# Wait for services to be healthy
sleep 30

# Run integration tests
./scripts/integration-tests.sh
```

## 📝 Documentation

Each feature branch has detailed README:

- **UEBlender**: `UnrealProject/Docs/`
- **HMI**: `IgnitionEdge/Docs/`
- **Web**: `backend/README.md`, `frontend/README.md`
- **AI**: `ai-service/README.md`

## 🛠️ Technologies

### Backend
- Spring Boot 3.2, Java 21
- Eclipse Milo 0.6 (OPC-UA)
- JWT (jjwt 0.12)
- Spring Security
- Maven

### Frontend
- React 18, TypeScript 5
- Vite 5, Recharts
- Axios, React Router 6
- Nginx (production)

### AI Service
- Node.js 20, Express 4
- Ollama (LLM)
- WebSocket (ws 8)
- Axios

### Visualization
- Unreal Engine 5.3
- Blender 4.0
- C++, open62541

### HMI
- Ignition Edge
- Perspective module
- TimeBase DB

## 🤝 Contributing

### Branch Naming
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Urgent production fixes
- `release/` - Release preparation

### Commit Messages
Follow Conventional Commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting
- `refactor:` - Code restructuring
- `test:` - Tests
- `chore:` - Maintenance

### Pull Request Process
1. Create feature branch from `develop`
2. Make changes and commit
3. Push to remote
4. Create PR to `develop`
5. Wait for review and CI checks
6. Merge after approval

## 📄 License

Part of VirtPLC project for Accenture internship challenge.

## 👥 Team

**Accenture VirtPLC Challenge 2025**

- UEBlender Subteam: Unreal Engine + Blender integration
- HMI Subteam: Ignition Edge configuration
- Web Subteam: Backend + Frontend development
- AI Subteam: Predictive analytics service

## 📧 Support

For issues and questions:
- Create GitHub issue
- Check documentation in respective feature branches
- Review Docker logs: `docker-compose logs -f [service]`

---

**Status**: ✅ All feature branches complete | 🐳 Docker Compose ready | 📦 Ready for deployment
