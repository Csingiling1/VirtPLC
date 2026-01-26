# VirtPLC Essen Demo - Quick Reference

## Quick Start Commands

```bash
# Navigate to essen-demo directory
cd /path/to/VirtPLC/essen-demo

# Make script executable (first time only)
chmod +x deploy-essen-demo.sh

# Run deployment
./deploy-essen-demo.sh
```

## Machine Type Reference

| Machine Type | Services | Ports | IP Variable |
|-------------|----------|-------|-------------|
| **Windows** | PLC Simulator | 5000, 5002 | PLC_IP |
| **Historian** | PostgreSQL, TimescaleDB | 15432, 15433 | HISTORIAN_IP |
| **AI (Main)** | Backend, Frontend, AI, Redis, Ollama | 3000, 18080, 3001, 6379, 11434 | MAIN_IP |
| **PLC** | Ignition, RabbitMQ, Node-RED | 8088, 1883, 15672, 1880 | PLC_IP |

## Common Management Commands

### View Status
```bash
# Check all services
docker-compose -f docker-compose.main.yml ps

# Check specific service
docker ps | grep backend
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.main.yml logs -f

# Specific service (last 100 lines)
docker-compose -f docker-compose.main.yml logs --tail=100 backend

# Follow logs in real-time
docker-compose -f docker-compose.main.yml logs -f frontend
```

### Service Control
```bash
# Restart all services
docker-compose -f docker-compose.main.yml restart

# Restart specific service
docker-compose -f docker-compose.main.yml restart ai-service

# Stop all services
docker-compose -f docker-compose.main.yml down

# Start services
docker-compose -f docker-compose.main.yml up -d
```

### Update Deployment
```bash
# Pull latest images
docker-compose -f docker-compose.main.yml pull

# Rebuild and restart
docker-compose -f docker-compose.main.yml up -d --build
```

## Access URLs

### Main AI PC
- **Frontend**: http://MAIN_IP:3000
- **Backend API**: http://MAIN_IP:18080
- **AI Service**: http://MAIN_IP:3001
- **Ollama API**: http://MAIN_IP:11434
- **Redis**: redis://MAIN_IP:6379

### PLC Machine
- **Ignition Gateway**: http://PLC_IP:8088
- **RabbitMQ Management**: http://PLC_IP:15672 (virtplc/virtplc123)
- **Node-RED**: http://PLC_IP:1880
- **MQTT Broker**: PLC_IP:1883

### Database Services
- **PostgreSQL**: HISTORIAN_IP:15432
- **TimescaleDB**: HISTORIAN_IP:15433

## Troubleshooting

### Check Service Health
```bash
# Backend health
curl http://MAIN_IP:18080/actuator/health

# AI service health
curl http://MAIN_IP:3001/health

# Simulator health
curl http://PLC_IP:5000/health
```

### Common Issues
```bash
# Port conflicts
netstat -tulpn | grep :3000

# Docker networks
docker network ls | grep virtplc

# Disk space
df -h

# Docker system cleanup
docker system prune -a
```

### Environment Configuration
```bash
# Edit environment file
nano .env.ai

# Reload environment
source .env.ai

# Restart affected services
docker-compose -f docker-compose.main.yml restart
```

## File Structure
```
essen-demo/
├── deploy-essen-demo.sh      # Main deployment script
├── DEPLOYMENT_TUTORIAL.md    # Full tutorial
├── docker-compose.main.yml   # Main services
├── docker-compose.data.yml   # Database services
├── docker-compose.plc.yml    # PLC services
├── docker-compose.simulator.yml  # Simulator services
└── .env.*                    # Environment files (created by script)
```

## Network Architecture

```
Windows Machine (192.168.1.102)
    ↓ PLC Simulator (5000)

PLC Machine (192.168.1.100)
    ↓ Ignition (8088)
    ↓ RabbitMQ (1883/15672)
    ↓ Node-RED (1880)

Historian Server (192.168.1.103)
    ↓ PostgreSQL (15432)
    ↓ TimescaleDB (15433)

Main AI PC (192.168.1.101)
    ↓ Frontend (3000)
    ↓ Backend (18080)
    ↓ AI Service (3001)
    ↓ Redis (6379)
    ↓ Ollama (11434)
    ↓ Go Collector
```

## Default Credentials

- **RabbitMQ**: virtplc / virtplc123
- **PostgreSQL**: virtplc / changeme
- **TimescaleDB**: virtplc / changeme
- **JWT Secret**: your-essen-demo-secret-key-change-in-production

## Performance Tips

1. **Monitor resource usage**: `docker stats`
2. **Check logs regularly**: Use log rotation
3. **Update images**: `docker-compose pull` weekly
4. **Backup data**: Regular database backups
5. **Network security**: Restrict port access

## Emergency Commands

```bash
# Stop everything immediately
docker-compose -f docker-compose.*.yml down

# Remove all containers and volumes
docker-compose -f docker-compose.*.yml down -v

# Complete system cleanup
docker system prune -a --volumes

# Reset networks
docker network prune
```</content>
<parameter name="filePath">/home/deginandor/Documents/Programming/VirtPLC/essen-demo/QUICK_REFERENCE.md