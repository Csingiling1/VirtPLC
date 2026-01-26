# VirtPLC Documentation Index

Comprehensive documentation for the VirtPLC Industrial IoT Platform.

## 📚 Quick Links

### Getting Started
- [Main README](../README.md) - Project overview and quick start
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute to VirtPLC
- [API Reference](./API_REFERENCE.md) - Complete API documentation

### Service Documentation
- [Collector Service](../collector/README.md) - MQTT to TimescaleDB ingestion
- [Node-RED Pipeline](../nodered/README.md) - Data enrichment and routing
- [NGINX Gateway](../nginx/README.md) - Reverse proxy and API gateway
- [Backend Service](../backend/README.md) - REST API service
- [AI Service](../ai-service/README.md) - AI-powered analytics
- [Frontend](../frontend/README.md) - Web application
- [HMI](../HMI/README.md) - Human-Machine Interface
- [Monitoring](../monitoring/README.md) - Observability stack

### Operations
- [Scripts](../scripts/README.md) - Utility and maintenance scripts
- [Cleanup Summary](./CLEANUP_SUMMARY.md) - Recent codebase improvements

## 📖 Documentation Index

### Architecture & Design
- [Architecture Overview](./ARCHITECTURE.ascii)
- [Architecture Diagram](./ARCHITECTURE_DIAGRAM.md)
- [Architecture Optimization](./ARCHITECTURE_OPTIMIZATION.md)
- [Protocol Optimization Guide](../PROTOCOL_OPTIMIZATION_GUIDE.md)
- [Orchestration Guide](./ORCHESTRATION.md)

### Deployment
- [Setup Guide](./Setup.md)
- [Kubernetes Quickstart](./deployment/KUBERNETES_QUICKSTART.md)
- [K8s Commands Reference](./deployment/K8S_COMMANDS.md)
- [K8s Visual Guide](./deployment/K8S_VISUAL_GUIDE.md)
- [Deployment Comparison](./deployment/DEPLOYMENT_COMPARISON.md)

### Security
- [Security Guide](../SECURITY.md)
- [OAuth2 Setup](./OAUTH2_SETUP.md)

### Data Management
- [Device Management](./DEVICE_MANAGEMENT.md)
- [Data Sources](../backend/DATA_SOURCES.md)
- [Tag Configuration](./Tag-Configuration.md)

### Integration
- [Integration Guide](./Integration.md)
- [HMI Design](./HMI-Design.md)
- [Ollama Models](./OLLAMA_MODELS.md)

### Testing
- [Testing Documentation](./testing/)

### Development
- [Scrum Board](./SCRUM_BOARD.md)
- [Sprint Planning](./sprints/)
- [Development Diary](./diary/)
- [Use Cases](./use-cases.md)

## 🎯 Common Tasks

### For New Contributors

1. Read [CONTRIBUTING.md](../CONTRIBUTING.md)
2. Review [Architecture Overview](./ARCHITECTURE_DIAGRAM.md)
3. Follow [Setup Guide](./Setup.md)
4. Check [API Reference](./API_REFERENCE.md)

### For Operators

1. Review [Deployment Guide](./deployment/KUBERNETES_QUICKSTART.md)
2. Set up [Monitoring](../monitoring/README.md)
3. Configure [Security](../SECURITY.md)
4. Learn [Maintenance Scripts](../scripts/README.md)

### For Developers

1. Study [Architecture](./ARCHITECTURE.ascii)
2. Understand [Data Pipeline](../nodered/README.md)
3. Review [API Documentation](./API_REFERENCE.md)
4. Follow [Coding Standards](../CONTRIBUTING.md#coding-standards)

### For API Users

1. Read [API Reference](./API_REFERENCE.md)
2. Review [Authentication Guide](./OAUTH2_SETUP.md)
3. Check [Integration Guide](./Integration.md)
4. See [API Examples](./api-documentation.html)

## 🔧 Service-Specific Guides

### Data Pipeline
```
Simulator → MQTT → Node-RED → Collector → TimescaleDB → Backend API
```

- [Simulator](../simulator/README.md)
- [Node-RED Pipeline](../nodered/README.md)
- [Collector Service](../collector/README.md)
- [Backend API](../backend/README.md)

### AI/Analytics
```
TimescaleDB → AI Service → Natural Language Interface
```

- [AI Service](../ai-service/README.md)
- [Ollama Models](./OLLAMA_MODELS.md)

### Frontend Stack
```
Browser → NGINX → Frontend (React) → Backend API
```

- [Frontend](../frontend/README.md)
- [NGINX](../nginx/README.md)

## 📊 Documentation Status

| Component | Status | Coverage |
|-----------|--------|----------|
| Main Project | ✅ Complete | 100% |
| Backend | ✅ Complete | 100% |
| Frontend | ✅ Complete | 100% |
| AI Service | ✅ Complete | 100% |
| Collector | ✅ Complete | 100% |
| Node-RED | ✅ Complete | 100% |
| NGINX | ✅ Complete | 100% |
| Scripts | ✅ Complete | 100% |
| HMI | ✅ Complete | 100% |
| Monitoring | ✅ Complete | 100% |
| Kubernetes | ✅ Complete | 100% |
| Infrastructure | ✅ Complete | 100% |
| API Reference | ✅ Complete | 100% |

## 🤝 Getting Help

- **Documentation Issues**: [Create an issue](https://github.com/Csingiling1/VirtPLC/issues)
- **General Questions**: Check existing documentation first
- **Contributions**: Follow [CONTRIBUTING.md](../CONTRIBUTING.md)

## 📝 Recent Updates

See [CLEANUP_SUMMARY.md](./CLEANUP_SUMMARY.md) for recent documentation improvements.

**Last Updated:** January 21, 2026

---

**Note:** All documentation is maintained in Markdown format for easy reading and contribution.
