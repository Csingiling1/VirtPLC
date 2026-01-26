# VirtPLC Essen Demo Deployment Tutorial

## Overview

The VirtPLC Essen Demo deployment script (`deploy-essen-demo.sh`) automates the deployment of the VirtPLC application across multiple machines in a distributed setup. It supports four different machine types and handles all the configuration automatically.

## Prerequisites

Before running the deployment script, ensure you have:

1. **Docker and Docker Compose installed**
   ```bash
   # Check installation
   docker --version
   docker-compose --version
   ```

2. **Git repository cloned**
   ```bash
   git clone https://github.com/Dedzsinator/VirtPLC.git
   cd VirtPLC/essen-demo
   ```

3. **Executable permissions on the script**
   ```bash
   chmod +x deploy-essen-demo.sh
   ```

## Architecture Overview

The deployment supports four machine types:

- **Windows Machine**: Python PLC Simulator only
- **Historian Server**: TimescaleDB + PostgreSQL databases
- **Main AI PC**: Backend, Frontend, AI Service, Redis, Ollama + Go Collector
- **PLC Machine**: Ignition, RabbitMQ, Node-RED

## Step-by-Step Deployment Guide

### Step 1: Navigate to the Essen Demo Directory

```bash
cd /path/to/VirtPLC/essen-demo
```

### Step 2: Run the Deployment Script

```bash
./deploy-essen-demo.sh
```

The script will start with a welcome message and prerequisite checks.

### Step 3: IP Address Detection

The script will attempt to auto-detect your local IP address. If it fails, you'll be prompted to enter it manually:

```
Detected local IP: 192.168.1.100
```

### Step 4: Select Machine Type

Choose your machine type from the menu:

```
================================
Machine Type Selection
================================
1) Windows Machine (Python PLC Simulator only)
2) Historian Server (TimescaleDB + PostgreSQL)
3) Main AI PC (Backend, Frontend, AI Service, Redis, Ollama + Go Collector)
4) PLC Machine (Ignition, RabbitMQ, Node-RED)
5) Auto-detect machine type
```

**Option 5 (Auto-detect)** is recommended for first-time users.

### Step 5: Configure Network Settings

Based on your machine type selection, you'll be prompted for IP addresses of other machines:

```
================================
IP Address Configuration
================================
Enter Windows Machine IP [192.168.1.102]:
Enter Historian Server IP [192.168.1.103]:
Enter PLC Machine IP [192.168.1.100]:
```

### Step 6: Review Configuration

The script will show your network configuration:

```
================================
Network Configuration for ai
================================
Local IP (Main Server): 192.168.1.101
Windows Machine IP: 192.168.1.102
Historian Server IP: 192.168.1.103
PLC Machine IP: 192.168.1.100

Services:
  Frontend: 192.168.1.101:3000
  Backend API: 192.168.1.101:18080
  AI Service: 192.168.1.101:3001
  ...
```

### Step 7: Confirm Deployment

Review the configuration and confirm:

```
Ready to deploy services? (y/N):
```

Type `y` and press Enter to start deployment.

### Step 8: Monitor Deployment

The script will:
- Create environment files (`.env.{machine_type}`)
- Set up Docker networks
- Start services using docker-compose
- Display service status

## Machine-Specific Deployment Examples

### Example 1: Main AI PC Deployment

```bash
# Run script and select option 3 (Main AI PC)
./deploy-essen-demo.sh

# Configure IPs:
# Windows Machine IP: 192.168.1.102
# Historian Server IP: 192.168.1.103
# PLC Machine IP: 192.168.1.100

# This will deploy:
# - Backend API (port 18080)
# - Frontend (port 3000)
# - AI Service (port 3001)
# - Redis (port 6379)
# - Ollama (port 11434)
# - Nginx (port 80)
# - Go Collector
```

### Example 2: PLC Machine Deployment

```bash
# Run script and select option 4 (PLC Machine)
./deploy-essen-demo.sh

# This will deploy:
# - Ignition Gateway (port 8088)
# - RabbitMQ MQTT (port 1883)
# - RabbitMQ Management (port 15672)
# - Node-RED (port 1880)
```

## Accessing the Deployed Application

After successful deployment, access your services:

### Main AI PC Services
- **Frontend**: http://YOUR_IP:3000
- **Backend API**: http://YOUR_IP:18080
- **AI Service**: http://YOUR_IP:3001
- **Ollama API**: http://YOUR_IP:11434

### PLC Machine Services
- **Ignition Gateway**: http://YOUR_IP:8088
- **RabbitMQ Management**: http://YOUR_IP:15672 (username: virtplc, password: virtplc123)
- **Node-RED**: http://YOUR_IP:1880

### Database Services (Historian Server)
- **PostgreSQL**: YOUR_IP:15432
- **TimescaleDB**: YOUR_IP:15433

## Managing Deployed Services

### View Logs
```bash
# View all service logs
docker-compose -f docker-compose.main.yml logs -f

# View specific service logs
docker-compose -f docker-compose.main.yml logs -f backend
```

### Stop Services
```bash
# Stop all services
docker-compose -f docker-compose.main.yml down

# Stop specific service
docker-compose -f docker-compose.main.yml stop backend
```

### Restart Services
```bash
# Restart all services
docker-compose -f docker-compose.main.yml restart

# Restart specific service
docker-compose -f docker-compose.main.yml restart frontend
```

### Update Deployment
```bash
# Pull latest images
docker-compose -f docker-compose.main.yml pull

# Rebuild and restart
docker-compose -f docker-compose.main.yml up -d --build
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Check if ports are already in use
   ```bash
   netstat -tulpn | grep :3000
   ```

2. **Network issues**: Verify Docker networks were created
   ```bash
   docker network ls | grep virtplc
   ```

3. **Service startup failures**: Check service logs
   ```bash
   docker-compose -f docker-compose.main.yml logs backend
   ```

4. **IP address changes**: Update environment files and restart services
   ```bash
   # Edit .env.ai file
   nano .env.ai
   # Then restart
   docker-compose -f docker-compose.main.yml restart
   ```

### Health Checks

The script includes health checks. You can manually verify service health:

```bash
# Check backend health
curl http://localhost:18080/actuator/health

# Check AI service health
curl http://localhost:3001/health

# Check simulator status
curl http://localhost:5000/health
```

## Configuration Files

The deployment creates several configuration files:

- `.env.{machine_type}`: Environment variables for your machine type
- `docker-compose.*.yml`: Service definitions for different components
- `collector.log`: Go collector logs (AI PC only)

## Security Notes

- Change default passwords in production
- Update JWT secrets in environment files
- Consider using Docker secrets for sensitive data
- Restrict network access to necessary ports only

## Next Steps

After deployment:
1. Access the frontend at http://YOUR_IP:3000
2. Configure PLC connections in Ignition
3. Set up data flows in Node-RED
4. Monitor system performance and logs

For detailed configuration of individual services, refer to the main VirtPLC documentation.</content>
<parameter name="filePath">/home/deginandor/Documents/Programming/VirtPLC/essen-demo/DEPLOYMENT_TUTORIAL.md