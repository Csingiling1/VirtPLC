# Web Branch - Setup Complete

## Summary
Complete foundational setup for Web Services subteam including Spring Boot backend with OPC-UA server and React TypeScript frontend with dashboard.

## Backend (Spring Boot 3 + Java 21)
- ✅ Maven project structure with pom.xml
- ✅ Main application class (VirtPlcApplication)
- ✅ OPC-UA server configuration (stub for Eclipse Milo)
- ✅ Node manager with simulated factory data
- ✅ REST API controllers (DataController, AuthController)
- ✅ JWT security utilities
- ✅ Data models (SensorData, AuthRequest/Response)
- ✅ Service layer (DataService)
- ✅ Spring Security configuration
- ✅ application.yml configuration
- ✅ Dockerfile for containerization

**Dependencies:**
- Spring Boot 3.2.0
- Eclipse Milo 0.6.10 (OPC-UA SDK)
- JWT (jjwt 0.12.3)
- Spring Security, Lombok, Validation

**Endpoints:**
- `POST /auth/login` - JWT token generation
- `GET /auth/validate` - Token validation
- `GET /api/data/latest` - Real-time sensor data
- `GET /api/data/range` - Historical data query
- `GET /api/data/health` - Health check

**OPC-UA Endpoint:** `opc.tcp://localhost:4840`

## Frontend (React 18 + TypeScript + Vite)
- ✅ Vite project configuration
- ✅ TypeScript setup (tsconfig.json)
- ✅ React Router for SPA navigation
- ✅ Login page with JWT authentication
- ✅ Live Metrics dashboard with Recharts
- ✅ HMI Embed page (Ignition iframe placeholder)
- ✅ API service layer with Axios
- ✅ useSensorData custom hook for polling
- ✅ Nginx configuration for Docker
- ✅ Dockerfile for containerization

**Dependencies:**
- React 18.2, React DOM, React Router 6
- TypeScript 5.2
- Vite 5 (build tool)
- Axios (HTTP client)
- Recharts (charting library)
- jwt-decode

**Routes:**
- `/login` - Authentication
- `/metrics` - Live factory data dashboard
- `/hmi` - HMI interface embed

## Architecture
```
Backend (Spring Boot)
├── OPC-UA Server (port 4840)      ← Unreal Engine, Ignition clients
├── REST API (port 8080)           ← Frontend, AI service
├── JWT Authentication
└── TimeBaseDB Integration (stub)

Frontend (React)
├── Vite Dev Server (port 3000)
├── Nginx (production)
├── API Client (Axios + JWT)
└── Real-time Charts (Recharts)
```

## Integration Points
- **OPC-UA Clients:** Ignition Edge, Unreal Engine → `opc.tcp://backend:4840`
- **Frontend → Backend:** REST API at `http://backend:8080`
- **TimeBase DB:** Port 8011 (configuration stub in application.yml)
- **AI Service:** Can consume `/api/data/latest` for predictions

## Docker
Both backend and frontend have Dockerfiles ready for containerization.

## Next Steps (for developers)
1. Run `npm install` in frontend/ (TypeScript errors are normal before packages are installed)
2. Run `mvn clean install` in backend/ to download dependencies
3. Implement full Eclipse Milo OPC-UA server (currently stub with simulated data)
4. Connect TimeBaseDB for historical data persistence
5. Implement user authentication database (currently demo mode)
6. Configure Ignition Edge and update HMI iframe URL
7. Add WebSocket support for real-time push notifications

## Commit Command
```bash
git add .
git commit -m "feat(web): Complete backend and frontend setup

- Spring Boot 3 backend with OPC-UA server stub
- REST API with JWT authentication
- React TypeScript frontend with Vite
- Live metrics dashboard with Recharts
- Dockerfiles for both services
- Comprehensive README and documentation"
```
