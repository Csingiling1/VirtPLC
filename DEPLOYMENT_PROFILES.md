# VirtPLC Multi-Profile Deployment

## Quick Start

VirtPLC now supports three deployment profiles to match your infrastructure needs:

### 1. Development Profile (Single Machine)
Everything runs on one computer (except Node-RED).

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env and set: DEPLOYMENT_PROFILE=dev

# Start services
./start.sh start

# Access at:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:18080
# - AI Service: http://localhost:3001
```

### 2. Stage2 Profile (Pre-Production - 2 Computers)
**Computer 1**: Main stack (collector, timescale, backend, frontend, ai-service)  
**Computer 2**: Unreal Engine + PLC with Node-RED

#### Computer 1 Setup
```bash
cp .env.example .env
# Edit .env:
#   DEPLOYMENT_PROFILE=stage2
#   PLC_HOST=192.168.1.100  (Computer 2 IP)
#   COMPUTER1_HOST=192.168.1.10  (This computer)

./start.sh start
```

#### Computer 2/PLC Setup
```bash
cd /opt/virtplc
cp -r nodered ./
# Edit .env for Node-RED configuration

docker-compose -f docker-compose.plc.yml --profile with-mqtt up -d

# Access Node-RED: http://<COMPUTER2_IP>:1880
```

### 3. Production Profile (3 Servers)
**Server 1 (Windows)**: PLC + Ignition Edge + Node-RED  
**Server 2 (Linux)**: Application stack (backend, frontend, ai-service)  
**Server 3 (Linux)**: TimescaleDB only

#### Server 3 (TimescaleDB) - Deploy First
```bash
cd /opt/virtplc
# Configure .env with TIMESCALE_PASSWORD
docker-compose -f docker-compose.timescale.yml up -d
```

#### Server 2 (Application Stack) - Deploy Second
```bash
cd /opt/virtplc
# Edit .env:
#   DEPLOYMENT_PROFILE=prod
#   SERVER1_HOST=192.168.1.10
#   SERVER2_HOST=192.168.1.20
#   SERVER3_HOST=192.168.1.30
#   TIMESCALE_PASSWORD=<from Server 3>

./start.sh start
```

#### Server 1 (Windows PLC) - Deploy Last
```powershell
cd C:\VirtPLC
# Configure Node-RED
docker-compose -f docker-compose.plc.yml --profile with-mqtt up -d
```

## File Structure

```
VirtPLC/
├── docker-compose.yml           # Base service definitions
├── docker-compose.dev.yml       # Development profile
├── docker-compose.stage2.yml    # Stage2 profile (Computer 1)
├── docker-compose.prod.yml      # Production profile (Server 2)
├── docker-compose.plc.yml       # PLC/Node-RED (Stage2 & Prod)
├── docker-compose.timescale.yml # TimescaleDB only (Prod Server 3)
├── .env.example                 # Environment template
├── start.sh                     # Deployment automation script
├── nodered/
│   ├── flows/
│   │   └── mqtt-opcua-bridge.json  # Pre-configured MQTT→OPC-UA flow
│   ├── settings.js              # Node-RED settings
│   └── package.json             # Node-RED dependencies
└── docs/deployment/
    └── MULTI_ENVIRONMENT_DEPLOYMENT.md  # Detailed documentation
```

## Node-RED MQTT to OPC-UA Bridge

The Node-RED flow is **plug-and-play** and automatically:

1. **Receives MQTT** from Unreal Engine on `unreal/factory/#` topics
2. **Parses** the payload and tag name
3. **Publishes** to OPC-UA server on port 4840
4. **Logs** all activities for debugging

### MQTT Topic Format
```
unreal/factory/{tagName}
```

Example:
```bash
# Publish from Unreal Engine or test manually:
mosquitto_pub -h <PLC_IP> -t "unreal/factory/temperature" -m '{"value":75.5}'
```

### OPC-UA Server Details
- **Port**: 4840
- **Endpoint**: `opc.tcp://<PLC_IP>:4840/`
- **Namespace**: `urn:virtplc:nodered`
- **Variables**: Auto-created from MQTT tag names

## Start Script Features

The `start.sh` script automates deployment:

```bash
./start.sh start      # Start services
./start.sh stop       # Stop services
./start.sh restart    # Restart services
./start.sh status     # Show status
./start.sh logs       # Show logs
./start.sh endpoints  # Show service URLs
./start.sh update     # Update images
./start.sh clean      # Remove everything
./start.sh menu       # Interactive menu (default)
```

## Key Changes Summary

### Docker Compose Structure
- **Base** (`docker-compose.yml`): Common service definitions
- **Overlays**: Profile-specific configurations
- **Usage**: `docker-compose -f docker-compose.yml -f docker-compose.{profile}.yml up`

### Profile Differences

| Feature | Dev | Stage2 | Production |
|---------|-----|--------|------------|
| Machines | 1 | 2 | 3 |
| Simulator | ✓ | ✗ (Real Unreal) | ✗ (Real PLC) |
| Node-RED | ✗ | Computer 2 | Server 1 |
| TimescaleDB | Local | Local | Server 3 |
| Ignition | Docker | ✗ | Server 1 (Real) |

### Environment Variables

Create `.env` from `.env.example` and configure:

```bash
# Required for all profiles
DEPLOYMENT_PROFILE=dev|stage2|prod
JWT_SECRET=<strong-secret>

# Stage2 specific
PLC_HOST=<Computer2_IP>
COMPUTER1_HOST=<Computer1_IP>

# Production specific
SERVER1_HOST=<Windows_Server_IP>
SERVER2_HOST=<Linux_App_Server_IP>
SERVER3_HOST=<Linux_DB_Server_IP>
TIMESCALE_PASSWORD=<strong-password>
```

## Network Ports

### Development (Single Machine)
- Frontend: 3000
- Backend API: 18080
- AI Service: 3001, 3002
- Databases: 15432 (Postgres), 15433 (TimescaleDB)
- Simulator: 5000
- Ignition: 8088

### Stage2 & Production
- **Computer 1 / Server 2**: Same as dev (except Ignition)
- **Computer 2 / Server 1**: 
  - Node-RED UI: 1880
  - OPC-UA: 4840
  - MQTT: 1883
  - Ignition: 8088 (Prod only)
- **Server 3 (Prod only)**:
  - TimescaleDB: 5432

## Verification

### Test Data Flow

1. **Publish MQTT** (on PLC/Computer 2)
```bash
docker exec plc-mqtt mosquitto_pub \
  -h localhost -t "unreal/factory/test_tag" \
  -m '{"value":123.45}'
```

2. **Check Node-RED** (on PLC)
- Access http://<PLC_IP>:1880
- Check Debug panel for messages

3. **Verify OPC-UA** (on Main Computer/Server 2)
```bash
docker logs virtplc-collector | grep "received"
```

4. **Query Database** (on Server 3 in Prod, or local)
```bash
docker exec virtplc-timescale psql -U virtplc -d virtplc_ts \
  -c "SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 5;"
```

## Documentation

See [`docs/deployment/MULTI_ENVIRONMENT_DEPLOYMENT.md`](docs/deployment/MULTI_ENVIRONMENT_DEPLOYMENT.md) for:
- Detailed architecture diagrams
- Network requirements and firewall rules
- Step-by-step deployment instructions
- Troubleshooting guide
- Maintenance procedures
- Security best practices

## Troubleshooting

### Services won't start
```bash
# Check Docker resources
docker system df

# Check logs
docker-compose logs

# Check specific service
docker logs <container_name>
```

### OPC-UA connection fails
```bash
# Test connectivity
telnet <PLC_IP> 4840

# Check Node-RED OPC-UA server
docker logs plc-nodered | grep "OPC UA Server"
```

### Data not flowing
```bash
# Check each hop:
# 1. MQTT published?
docker logs plc-mqtt | grep "PUBLISH"

# 2. Node-RED receiving?
docker logs plc-nodered | grep "mqtt"

# 3. Collector receiving OPC-UA?
docker logs virtplc-collector | grep "received"

# 4. Data in database?
docker exec virtplc-timescale psql -U virtplc -d virtplc_ts \
  -c "SELECT COUNT(*) FROM sensor_data WHERE timestamp > NOW() - INTERVAL '5 minutes';"
```

## Migration from Old Setup

If you have an existing deployment:

```bash
# 1. Backup data
docker-compose down
sudo tar -czf virtplc-backup.tar.gz /var/lib/docker/volumes/virtplc-*

# 2. Pull latest code
git pull

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Start with new profile
./start.sh start
```

## Support

- **Documentation**: [`/docs`](docs/) directory
- **Issues**: GitHub Issues
- **Logs**: `./start.sh logs`

---

**Last Updated**: December 5, 2025  
**Version**: 2.0 (Multi-Profile Architecture)
