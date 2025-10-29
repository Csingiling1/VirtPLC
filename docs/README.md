# AI-Driven Digital Twin for Smart Warehouses

> **Note:** The project documentation has been organized into separate files for better clarity and navigation.

## Documentation Structure

This project documentation is organized into the following files:

- **[concept.md](./concept.md)** - Main concept, hardware requirements, system flow, and MVP features
- **[use-case-diagram.md](./use-cases.md)** - Use cases
- **[sprint1-summary.md](./sprints/sprint1-summary.md)** - Summary of Sprint 1 achievements, metrics, and retrospectives
- **[sprint2-backlog.md](./sprints/sprint2-backlog.md)** - Sprint 2 backlog with tasks, use cases, and team assignments

---

## Quick Summary

VirtPLC is a comprehensive **industrial automation platform** that creates a virtual PLC (Programmable Logic Controller) ecosystem for factory automation. It provides a complete microservices-based solution for monitoring, controlling, and optimizing industrial processes through AI-enhanced predictive maintenance and real-time data analytics.

The system integrates:

- **HMI/SCADA Interface** (Ignition Edge) - Real-time operator dashboards
- **AI-Powered Analytics** (FastAPI + Ollama LLM) - Predictive maintenance and anomaly detection
- **Enterprise Backend** (Java Spring Boot) - REST APIs, OPC-UA server, JWT authentication
- **Time-Series Database** (TimescaleDB) - High-performance sensor data storage
- **Relational Database** (PostgreSQL) - Business data and configuration
- **PLC Simulation** - Virtual PLC for testing and development
- **Monitoring Stack** (Grafana + Prometheus) - System observability and alerting

This creates a **production-ready industrial IoT platform** that enables manufacturers to monitor equipment health, predict failures, optimize maintenance schedules, and make data-driven decisions - all within a scalable, containerized microservices architecture.

### Key Features

- **Real-time PLC Data**: OPC-UA communication with industrial equipment
- **AI-Powered Insights**: LLM-based analysis of sensor data and equipment behavior
- **Predictive Maintenance**: Machine learning models for failure prediction
- **Scalable Architecture**: Docker Compose orchestration with Kubernetes-ready design
- **Production Monitoring**: Comprehensive observability with Grafana dashboards
- **Multi-tenant Ready**: JWT authentication and role-based access control

### Technology Stack

- **Frontend**: React + Vite + TypeScript
- **Backend**: Java Spring Boot + PostgreSQL + TimescaleDB
- **AI Service**: FastAPI + Ollama (LLaMA 3.2 models)
- **HMI**: Ignition Edge Gateway
- **Infrastructure**: Docker + Docker Compose + Nginx
- **Monitoring**: Grafana + Prometheus + Loki
