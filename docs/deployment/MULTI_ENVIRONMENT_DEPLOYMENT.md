# VirtPLC Multi-Environment Deployment Guide

## Overview

VirtPLC supports three deployment profiles:
1. **Development (dev)** - Single machine, all services
2. **Stage2 (pre-production)** - 2 computers setup
3. **Production (prod)** - 3 servers setup

## Architecture Diagrams

### Development Profile (Single Machine)
```
┌─────────────────────────────────────────────────────────┐
│                    Computer 1 (Dev)                      │
│                                                          │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐              │
│  │Simulator│  │ Backend  │  │ Frontend │              │
│  │         │  │          │  │          │              │
│  └────┬────┘  └────┬─────┘  └────┬─────┘              │
│       │            │             │                      │
│  ┌────┴────────────┴─────────────┴─────┐               │
│  │         TimescaleDB + Postgres       │               │
│  └──────────────────────────────────────┘               │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │AI Service│  │  Redis   │  │ Collector│              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                          │
│  Note: Node-RED is excluded in dev profile              │
└─────────────────────────────────────────────────────────┘
```

### Stage2 Profile (Pre-Production - 2 Computers)
```
┌────────────────────────────┐     ┌────────────────────────────┐
│   Computer 2 (PLC/Unreal)  │     │    Computer 1 (Main Stack) │
│                            │     │                            │
│  ┌──────────────────┐      │     │  ┌──────────┐             │
│  │  Unreal Engine   │      │     │  │ Backend  │             │
│  │  (Factory Sim)   │      │     │  └────┬─────┘             │
│  └────────┬─────────┘      │     │       │                    │
│           │ MQTT           │     │  ┌────┴──────────┐         │
│  ┌────────▼─────────┐      │     │  │  TimescaleDB  │         │
│  │  MQTT Broker     │      │     │  └───────────────┘         │
│  │   (Optional)     │      │     │                            │
│  └────────┬─────────┘      │     │  ┌──────────┐             │
│           │                │     │  │ Frontend │             │
│  ┌────────▼─────────┐      │     │  └──────────┘             │
│  │    Node-RED      │      │     │                            │
│  │ MQTT → OPC-UA    │◄─────┼─────┤  ┌──────────┐             │
│  │  Bridge (4840)   │      │     │  │Collector │             │
│  └──────────────────┘      │     │  │(OPC-UA   │             │
│                            │     │  │ Client)  │             │
│  PLC or Embedded Device    │     │  └──────────┘             │
└────────────────────────────┘     │                            │
                                   │  ┌──────────┐             │
                                   │  │AI Service│             │
                                   │  └──────────┘             │
                                   └────────────────────────────┘
```

### Production Profile (3 Servers)
```
┌────────────────────────┐     ┌────────────────────────┐     ┌──────────────────┐
│  Server 1 (Windows)    │     │  Server 2 (Linux)      │     │ Server 3 (Linux) │
│                        │     │                        │     │                  │
│  ┌──────────────────┐  │     │  ┌──────────┐         │     │  ┌────────────┐  │
│  │   Real PLC       │  │     │  │ Backend  │         │     │  │TimescaleDB │  │
│  │                  │  │     │  └────┬─────┘         │     │  │            │  │
│  └────────┬─────────┘  │     │       │               │     │  │(Dedicated) │  │
│           │            │     │  ┌────┴──────┐        │     │  └──────▲─────┘  │
│  ┌────────▼─────────┐  │     │  │ Postgres  │        │     │         │        │
│  │ Ignition Edge    │  │     │  └───────────┘        │     │         │        │
│  │                  │  │     │                        │     │         │        │
│  └────────┬─────────┘  │     │  ┌──────────┐         │     │         │        │
│           │ MQTT       │     │  │ Frontend │         │     │         │        │
│  ┌────────▼─────────┐  │     │  └──────────┘         │     │         │        │
│  │    Node-RED      │  │     │                        │     │         │        │
│  │ MQTT → OPC-UA    │◄─┼─────┤  ┌──────────┐         │     │         │        │
│  │  Bridge (4840)   │  │     │  │Collector │─────────┼─────┴─────────┘        │
│  └──────────────────┘  │     │  │(OPC-UA   │         │                        │
│                        │     │  │ Client)  │         │                        │
│                        │     │  └──────────┘         │                        │
│                        │     │                        │                        │
│                        │     │  ┌──────────┐         │                        │
│                        │     │  │AI Service│─────────┼────────────────────────┘
│                        │     │  └──────────┘         │
└────────────────────────┘     └────────────────────────┘
```

## Prerequisites

### All Environments
- Docker Engine 24.0+
- Docker Compose 2.20+
- Network connectivity between machines (for multi-machine setups)

### Development
- 16GB RAM minimum
- 4 CPU cores minimum

### Stage2 & Production
- Computer/Server specifications per profile
- Static IP addresses configured
- Firewall rules configured (see Network Requirements)

## Network Requirements

### Ports by Service

| Service | Port | Protocol | Required In |
|---------|------|----------|-------------|
| Backend API | 18080 | TCP | All |
| Frontend | 3000 | TCP | All |
| AI Service API | 3001 | TCP | All |
| AI Service WS | 3002 | TCP | All |
| PostgreSQL | 15432 | TCP | Dev, Stage2, Prod (Server 2) |
| TimescaleDB | 15433 | TCP | Dev, Stage2 |
| TimescaleDB | 5432 | TCP | Prod (Server 3) |
| Node-RED UI | 1880 | TCP | Stage2, Prod (PLC) |
| Node-RED OPC-UA | 4840 | TCP | Stage2, Prod (PLC) |
| MQTT | 1883 | TCP | Dev, Stage2, Prod |
| Ignition | 8088 | TCP | Prod (Server 1) |
| Ollama | 11434 | TCP | All |
| Redis | 6379 | TCP | All |

### Firewall Configuration

#### Stage2 - Computer 1 (Allow Inbound)
```bash
# OPC-UA from Computer 2
sudo ufw allow from <COMPUTER2_IP> to any port 4840 proto tcp
# Optional: Web UI access
sudo ufw allow 3000/tcp
sudo ufw allow 18080/tcp
```

#### Stage2 - Computer 2/PLC (Allow Inbound)
```bash
# Node-RED UI access
sudo ufw allow 1880/tcp
# OPC-UA server
sudo ufw allow 4840/tcp
# MQTT (if local broker)
sudo ufw allow 1883/tcp
```

#### Production - Server 1 (Allow Inbound)
```bash
# Node-RED
sudo ufw allow 1880/tcp
sudo ufw allow 4840/tcp
# Ignition
sudo ufw allow 8088/tcp
sudo ufw allow 8043/tcp
```

#### Production - Server 2 (Allow Inbound)
```bash
# Backend API
sudo ufw allow 18080/tcp
# Frontend
sudo ufw allow 3000/tcp
# AI Service
sudo ufw allow 3001/tcp
sudo ufw allow 3002/tcp
```

#### Production - Server 3 (Allow Inbound)
```bash
# TimescaleDB from Server 2 only
sudo ufw allow from <SERVER2_IP> to any port 5432 proto tcp
```

## Deployment Instructions

### 1. Development Profile (Single Machine)

#### Setup
```bash
cd /path/to/VirtPLC

# Set environment variables (optional)
cp .env.example .env
# Edit .env with your values

# Start all services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
```

#### Verify Deployment
```bash
# Check all services are running
docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps

# Test endpoints
curl http://localhost:18080/actuator/health  # Backend
curl http://localhost:3000                    # Frontend
curl http://localhost:3001/health             # AI Service
```

### 2. Stage2 Profile (2 Computers)

#### Computer 1 (Main Stack) Setup
```bash
cd /path/to/VirtPLC

# Create .env file
cat > .env << EOF
PLC_HOST=192.168.1.100  # Computer 2 IP address
COMPUTER1_HOST=192.168.1.10  # This computer's IP
EOF

# Start services
docker-compose -f docker-compose.yml -f docker-compose.stage2.yml up -d

# Monitor logs
docker-compose -f docker-compose.yml -f docker-compose.stage2.yml logs -f collector
```

#### Computer 2/PLC (Node-RED Bridge) Setup
```bash
cd /path/to/VirtPLC

# Copy Node-RED configuration
mkdir -p /opt/virtplc
cp -r nodered /opt/virtplc/
cp docker-compose.plc.yml /opt/virtplc/

cd /opt/virtplc

# Configure environment
cat > .env << EOF
MQTT_BROKER=localhost  # or external MQTT broker IP
MQTT_PORT=1883
NODE_RED_CREDENTIAL_SECRET=$(openssl rand -hex 32)
DEPLOYMENT_ENV=stage2
EOF

# Start Node-RED (with local MQTT)
docker-compose -f docker-compose.plc.yml --profile with-mqtt up -d

# OR Start Node-RED (without local MQTT, using external broker)
docker-compose -f docker-compose.plc.yml up -d

# Access Node-RED UI
# http://<COMPUTER2_IP>:1880
# Default credentials: admin / password (change in production!)
```

#### Configure Unreal Engine MQTT
In your Unreal Engine project, configure MQTT client:
```cpp
// MQTT Settings
Broker: <COMPUTER2_IP or MQTT_BROKER_IP>
Port: 1883
Topic Prefix: unreal/factory/
```

#### Verify Stage2 Deployment
```bash
# On Computer 1 - Check OPC-UA connection
docker logs virtplc-collector | grep "Connected to OPC-UA"

# On Computer 2 - Check Node-RED
docker logs plc-nodered | grep "Started flows"

# Test MQTT → OPC-UA flow
# On Computer 2:
docker exec plc-mqtt mosquitto_pub -h localhost -t "unreal/factory/test_tag" \
  -m '{"value":123.45,"quality":"GOOD"}'

# On Computer 1 - Check if data arrived
docker exec virtplc-timescale psql -U virtplc -d virtplc_ts \
  -c "SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 5;"
```

### 3. Production Profile (3 Servers)

#### Server 3 (TimescaleDB) Setup - Deploy First
```bash
# On Server 3
cd /opt/virtplc
mkdir -p /data/timescale  # Dedicated storage mount point

# Create .env
cat > .env << EOF
TIMESCALE_PASSWORD=$(openssl rand -base64 32)
EOF

# Save password for other servers!
echo "TIMESCALE_PASSWORD: $(cat .env | grep TIMESCALE_PASSWORD)" > /root/timescale-credentials.txt

# Start TimescaleDB
docker-compose -f docker-compose.timescale.yml up -d

# Verify
docker logs virtplc-timescale
docker exec virtplc-timescale pg_isready -U virtplc -d virtplc_ts
```

#### Server 2 (Application Stack) Setup - Deploy Second
```bash
# On Server 2
cd /opt/virtplc

# Create .env with all configurations
cat > .env << EOF
# Server IPs
SERVER1_HOST=192.168.1.10  # Windows PLC server
SERVER2_HOST=192.168.1.20  # This server
SERVER3_HOST=192.168.1.30  # TimescaleDB server

# Database passwords (get from Server 3)
TIMESCALE_PASSWORD=<password-from-server3>
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# JWT Secret
JWT_SECRET=$(openssl rand -base64 64)
EOF

# Start application stack
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Monitor startup
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
```

#### Server 1 (Windows PLC + Node-RED) Setup - Deploy Last
```powershell
# On Server 1 (Windows with Docker Desktop)
cd C:\VirtPLC

# Copy Node-RED configuration
mkdir nodered
# Copy nodered folder contents from repository

# Create .env
@"
MQTT_BROKER=localhost
MQTT_PORT=1883
NODE_RED_CREDENTIAL_SECRET=$(([System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Random)))))
DEPLOYMENT_ENV=production
"@ | Out-File -FilePath .env -Encoding ASCII

# Start Node-RED with local MQTT
docker-compose -f docker-compose.plc.yml --profile with-mqtt up -d
```

#### Configure Ignition Edge on Server 1
1. Install Ignition Edge on Windows
2. Connect to PLC hardware
3. Configure OPC-UA client in Ignition:
   - Server URL: `opc.tcp://localhost:4840`
   - Node-RED OPC-UA server
4. Enable MQTT transmission module
5. Configure MQTT publisher:
   - Broker: `localhost:1883`
   - Topic: `unreal/factory/{tagName}`

#### Verify Production Deployment
```bash
# On Server 3 - Check TimescaleDB
docker exec virtplc-timescale psql -U virtplc -d virtplc_ts -c "\dt"

# On Server 2 - Check application connectivity
docker logs virtplc-backend | grep "Connected to database"
docker logs virtplc-collector | grep "Connected to OPC-UA"
docker logs virtplc-ai | grep "Connected to TimescaleDB"

# Test end-to-end flow
# Server 1: Publish MQTT from Ignition or Node-RED test inject
# Server 2: Check collector logs
# Server 3: Query TimescaleDB for new data
```

## Node-RED Configuration

### First-Time Setup

1. Access Node-RED UI:
   - Dev: `http://localhost:1880`
   - Stage2/Prod: `http://<PLC_IP>:1880`

2. Login with default credentials:
   - Username: `admin`
   - Password: `password` (change immediately!)

3. The MQTT to OPC-UA bridge flow is pre-installed

4. Verify flow is active:
   - Check MQTT In node is connected
   - Check OPC-UA Server node shows "connected"
   - Use Test Inject node to verify data flow

### MQTT Topics Structure

```
unreal/factory/
├── conveyor_speed          # Float
├── machine_temperature     # Float
├── production_count        # Integer
├── alarm_status           # Boolean
└── ...                    # Other tags
```

### OPC-UA Address Space

Node-RED creates OPC-UA variables:
```
Root
└── Objects
    └── urn:virtplc:nodered
        ├── conveyor_speed
        ├── machine_temperature
        ├── production_count
        └── ...
```

### Testing the Bridge

#### Test 1: MQTT Publish
```bash
# On PLC/Node-RED machine
docker exec plc-mqtt mosquitto_pub \
  -h localhost \
  -t "unreal/factory/test_tag" \
  -m '{"value":123.45,"quality":"GOOD","timestamp":"2025-12-05T10:00:00Z"}'
```

#### Test 2: OPC-UA Read
```bash
# On collector machine (Server 2)
docker logs virtplc-collector -f
# Should show incoming OPC-UA values
```

#### Test 3: End-to-End
```bash
# Publish test data
docker exec plc-mqtt mosquitto_pub \
  -h localhost -t "unreal/factory/temperature" -m '75.5'

# Check in TimescaleDB
docker exec virtplc-timescale psql -U virtplc -d virtplc_ts \
  -c "SELECT * FROM sensor_data WHERE tag_name='temperature' ORDER BY timestamp DESC LIMIT 1;"
```

## Troubleshooting

### Development Issues

**Problem**: Services won't start
```bash
# Check for port conflicts
sudo netstat -tulpn | grep -E '(8080|3000|5432)'

# Check Docker resources
docker system df
docker system prune  # if needed
```

**Problem**: Cannot connect to services
```bash
# Check all services are healthy
docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps

# Check specific service logs
docker logs virtplc-backend
```

### Stage2 Issues

**Problem**: OPC-UA connection fails from Computer 1 to Computer 2
```bash
# On Computer 1, test connectivity
telnet <COMPUTER2_IP> 4840

# Check Node-RED OPC-UA server status
docker exec plc-nodered cat /data/logs/audit.log
```

**Problem**: MQTT messages not reaching Node-RED
```bash
# Subscribe to MQTT topic on Computer 2
docker exec plc-mqtt mosquitto_sub -h localhost -t "unreal/factory/#" -v

# Check Node-RED debug output
# Access http://<COMPUTER2_IP>:1880 and check Debug panel
```

### Production Issues

**Problem**: TimescaleDB connection fails from Server 2
```bash
# On Server 2, test connectivity to Server 3
telnet <SERVER3_IP> 5432

# Check TimescaleDB is accepting connections
# On Server 3:
docker exec virtplc-timescale psql -U virtplc -d virtplc_ts -c "SHOW listen_addresses;"
```

**Problem**: Data not flowing end-to-end
```bash
# Check each hop:

# 1. Server 1 - MQTT published?
docker logs plc-mqtt | grep "PUBLISH"

# 2. Server 1 - Node-RED receiving?
docker logs plc-nodered | grep "mqtt"

# 3. Server 1 - OPC-UA server running?
docker logs plc-nodered | grep "OPC UA Server"

# 4. Server 2 - Collector receiving OPC-UA?
docker logs virtplc-collector | grep "received"

# 5. Server 3 - Data in TimescaleDB?
docker exec virtplc-timescale psql -U virtplc -d virtplc_ts \
  -c "SELECT COUNT(*) FROM sensor_data WHERE timestamp > NOW() - INTERVAL '5 minutes';"
```

## Maintenance

### Backups

#### Development
```bash
# Backup all volumes
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
sudo tar -czf virtplc-backup-$(date +%Y%m%d).tar.gz \
  /var/lib/docker/volumes/virtplc-*
```

#### Production - TimescaleDB (Server 3)
```bash
# Automated backup script
docker exec virtplc-timescale pg_dump \
  -U virtplc \
  -d virtplc_ts \
  -F c \
  -f /backup/virtplc_ts_$(date +%Y%m%d_%H%M%S).dump

# Restore
docker exec virtplc-timescale pg_restore \
  -U virtplc \
  -d virtplc_ts \
  -c \
  /backup/virtplc_ts_YYYYMMDD_HHMMSS.dump
```

### Updates

```bash
# Pull latest images
docker-compose pull

# Rebuild custom images
docker-compose build --no-cache

# Rolling update (minimal downtime)
docker-compose up -d --no-deps --build <service_name>
```

### Monitoring

#### Health Checks
```bash
# All services
docker-compose ps

# Specific service health
docker inspect --format='{{.State.Health.Status}}' virtplc-backend
```

#### Logs
```bash
# Follow all logs
docker-compose logs -f

# Specific service
docker logs -f --tail=100 virtplc-backend

# Search logs
docker logs virtplc-collector 2>&1 | grep ERROR
```

## Environment Variables Reference

### Global Variables
| Variable | Description | Default | Required In |
|----------|-------------|---------|-------------|
| PROFILE | Deployment profile | dev | All |
| JWT_SECRET | JWT signing key | - | All |

### Stage2 Specific
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| PLC_HOST | Computer 2/PLC IP | 192.168.1.100 | Yes |
| COMPUTER1_HOST | Computer 1 IP | 192.168.1.10 | Yes |

### Production Specific
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| SERVER1_HOST | Windows PLC Server | 192.168.1.10 | Yes |
| SERVER2_HOST | Linux App Server | 192.168.1.20 | Yes |
| SERVER3_HOST | TimescaleDB Server | 192.168.1.30 | Yes |
| TIMESCALE_PASSWORD | DB password | - | Yes |
| POSTGRES_PASSWORD | DB password | - | Yes |

## Security Considerations

### Production Checklist
- [ ] Change all default passwords
- [ ] Use strong JWT_SECRET
- [ ] Enable HTTPS for public endpoints
- [ ] Configure firewall rules
- [ ] Enable Docker security scanning
- [ ] Implement network segmentation
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] Access control (RBAC)

### Node-RED Security
```bash
# Generate password hash
docker exec plc-nodered node -e \
  "console.log(require('bcryptjs').hashSync('your-new-password', 8))"

# Update settings.js with new hash
```

## Support

For issues and questions:
- GitHub Issues: [VirtPLC Repository]
- Documentation: `/docs` directory
- Logs: Check service-specific logs

## Next Steps

After deployment:
1. Configure Unreal Engine MQTT client
2. Set up Ignition Edge (production)
3. Configure monitoring and alerts
4. Set up automated backups
5. Performance tuning based on load
6. Security hardening
