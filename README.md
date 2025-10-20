# VirtPLC - Backend & Frontend

**Branch:** `feature/Web` | **Subteam:** Web Services | **Accenture Challenge**

This branch contains the Spring Boot backend (OPC-UA server, REST API, JWT auth) and React TypeScript frontend (dashboard, live metrics, HMI integration).

## Overview

Data infrastructure providing OPC-UA server, REST APIs, time-series storage, and web dashboard for factory monitoring and control.

## Project Structure

```
backend/                # Spring Boot 3 application
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/virtplc/
│   │   │       ├── config/      # Spring configuration
│   │   │       ├── opcua/       # OPC-UA server (Milo)
│   │   │       ├── api/         # REST controllers
│   │   │       ├── service/     # Business logic
│   │   │       ├── model/       # Data models
│   │   │       └── security/    # JWT authentication
│   │   └── resources/
│   │       └── application.yml  # Configuration
│   └── test/
├── pom.xml             # Maven dependencies
└── Dockerfile

frontend/               # React application
├── src/
│   ├── components/     # React components
│   ├── pages/          # Page components
│   ├── services/       # API clients
│   ├── hooks/          # Custom hooks
│   └── App.tsx         # Main app
├── package.json
└── Dockerfile

docs/                   # Documentation
├── API.md              # REST API documentation
├── Setup.md            # Setup instructions
└── Development.md      # Development guide
```

## Quick Start

### Backend

```bash
cd backend
./mvnw spring-boot:run
```

Access at `http://localhost:8080`

OPC-UA server at `opc.tcp://localhost:4840`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Access at `http://localhost:3000`

## Features

### Backend
- OPC-UA server (Eclipse Milo)
- REST API (Spring Boot 3, Java 21)
- JWT authentication
- TimeBaseDB integration
- Real-time data endpoints
- Historical data queries

### Frontend
- React 18 + TypeScript
- Live metrics dashboard
- HMI iframe embed
- JWT authentication
- Chart visualizations
- Responsive design

## Documentation

- **API.md** - REST API endpoints and examples
- **Setup.md** - Installation and configuration
- **Development.md** - Development guidelines
