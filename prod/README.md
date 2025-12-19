# VirtPLC Production Deployment - 3 Server Setup

This directory contains Docker Compose files for deploying VirtPLC across 3 separate servers/computers in a production environment.

## Architecture Overview

- **Historian Server (Server 3)**: TimescaleDB + MCP Server for time-series data and AI access
- **PLC-AI Server (Server 2)**: Backend services, AI, frontend, and data collection
- **PLC Server (Server 1)**: PLC simulator, Ignition HMI, Node-RED, and MQTT broker

All servers communicate over a shared Docker network with static IP addresses.

## Network Configuration

All services run on the `192.168.1.0/24` subnet. Default IP assignments:

### Historian Server (historian-compose.yml)
- TimescaleDB: `192.168.1.30`
- MCP Server: `192.168.1.31`
- Cleanup Service: `192.168.1.32`

### PLC-AI Server (plc-ai-compose.yml)
- Backend: `192.168.1.20`
- Frontend: `192.168.1.21`
- Ollama: `192.168.1.22`
- Ollama Init: `192.168.1.23`
- AI Service: `192.168.1.24`
- PostgreSQL: `192.168.1.25`
- Redis: `192.168.1.26`
- Collector: `192.168.1.27`

### PLC Server (plc-compose.yml)
- Simulator: `192.168.1.10`
- Simulator Monitor: `192.168.1.11`
- Ignition: `192.168.1.12`
- MQTT: `192.168.1.13`
- Node-RED: `192.168.1.14`

## Environment Variables

Create a `.env` file in this directory or set environment variables:

```bash
# Server IP Configuration
HISTORIAN_IP=192.168.1.30
PLC_AI_IP=192.168.1.20
PLC_IP=192.168.1.10

# Service IPs (optional - defaults provided)
MCP_IP=192.168.1.31
FRONTEND_IP=192.168.1.21
OLLAMA_IP=192.168.1.22
AI_IP=192.168.1.24
POSTGRES_IP=192.168.1.25
REDIS_IP=192.168.1.26
COLLECTOR_IP=192.168.1.27
SIMULATOR_MONITOR_IP=192.168.1.11
IGNITION_IP=192.168.1.12
MQTT_IP=192.168.1.13
NODERED_IP=192.168.1.14

# Port Configuration (optional)
TIMESCALE_PORT=15433
BACKEND_PORT=18080
FRONTEND_PORT=3000
AI_PORT=3001
POSTGRES_PORT=15432
SIMULATOR_PORT=5000
IGNITION_PORT=8088
MQTT_PORT=1883
NODERED_PORT=1880

# Database Configuration
TIMESCALE_PASSWORD=changeme
POSTGRES_PASSWORD=changeme

# AI Configuration
CLAUDE_API_KEY=your-claude-api-key-here

# MQTT Configuration
MQTT_USERNAME=virtplc
MQTT_PASSWORD=virtplc123

# Security
JWT_SECRET=your-secret-key-change-in-production
NODE_RED_CREDENTIAL_SECRET=your-secret-key
IGNITION_USERNAME=admin
IGNITION_PASSWORD=password
```

## Deployment Instructions

### Step 1: Configure Network
Ensure all three servers can communicate on the `192.168.1.0/24` network. You may need to:
- Configure static IPs on each server
- Set up routing between servers
- Configure firewall rules to allow communication

### Step 2: Start Historian Server (Server 3)
```bash
# On Historian server
cd /path/to/VirtPLC/prod
docker-compose -f historian-compose.yml up -d
```

### Step 3: Start PLC-AI Server (Server 2)
```bash
# On PLC-AI server
cd /path/to/VirtPLC/prod
docker-compose -f plc-ai-compose.yml up -d
```

### Step 4: Start PLC Server (Server 1)
```bash
# On PLC server
cd /path/to/VirtPLC/prod
docker-compose -f plc-compose.yml up -d
```

## Service Access

### Historian Server
- TimescaleDB: `postgresql://virtplc:changeme@${HISTORIAN_IP}:15433/virtplc_ts`
- MCP Server: `http://${MCP_IP}:9092`

### PLC-AI Server
- Frontend: `http://${FRONTEND_IP}:3000`
- Backend API: `http://${PLC_AI_IP}:18080`
- AI Service: `http://${AI_IP}:3001`
- PostgreSQL: `postgresql://virtplc:changeme@${POSTGRES_IP}:15432/virtplc`

### PLC Server
- Simulator: `http://${PLC_IP}:5000`
- Simulator Monitor: `http://${SIMULATOR_MONITOR_IP}:5002`
- Ignition HMI: `http://${IGNITION_IP}:8088`
- Node-RED: `http://${NODERED_IP}:1880`
- MQTT: `${MQTT_IP}:1883`

## Monitoring and Troubleshooting

### Check Service Health
```bash
# On each server, check running containers
docker ps

# Check network connectivity
docker network inspect virtplc-network
```

### View Logs
```bash
# View logs for a specific service
docker-compose -f <compose-file> logs <service-name>

# Follow logs in real-time
docker-compose -f <compose-file> logs -f <service-name>
```

### Common Issues

1. **Network Connectivity**: Ensure all servers can reach each other on the 192.168.1.0/24 network
2. **Port Conflicts**: Check that the configured ports are available on each server
3. **Volume Permissions**: Ensure Docker has permissions to create and access volumes
4. **Environment Variables**: Verify all required environment variables are set

## Scaling and High Availability

For production environments, consider:
- Load balancers for frontend and backend services
- Database replication for TimescaleDB and PostgreSQL
- Redis clustering for caching
- Monitoring with Prometheus/Grafana
- Backup strategies for databases and volumes

## Security Considerations

- Change all default passwords
- Use HTTPS/TLS for external access
- Implement proper firewall rules
- Regularly update Docker images
- Use secrets management for sensitive data
- Monitor access logs and implement rate limiting