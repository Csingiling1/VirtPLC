# Essen Demo - Multi-Computer VirtPLC Deployment

This directory contains Docker Compose configurations for deploying VirtPLC across multiple computers for the Essen demonstration.

## Architecture Overview

The VirtPLC system is split across four computers:

1. **PLC** (PLC machine)
   - Components: Ignition Edge, Node-RED, RabbitMQ
   - Purpose: PLC simulation and data collection

2. **Historian Server** (Server with PostgreSQL and TimescaleDB)
   - Components: TimescaleDB, PostgreSQL
   - Purpose: Time-series data storage and relational database

3. **Main AI PC** (Linux server)
   - Components: Collector, Backend, Frontend, MCP, AI Service
   - Purpose: Main application logic, APIs, and user interfaces

4. **Windows Machine** (Gaming PC with Unreal Engine)
   - Components: Python PLC Simulator
   - Purpose: Run PLC simulator alongside Unreal Engine

## Network Configuration

Each computer uses different subnets:
- PLC Network: `172.20.0.0/16`
- Data Network: `172.21.0.0/16`
- Main Network: `172.22.0.0/16`

## Deployment Instructions

### Step 1: PLC Setup
On the PLC machine:

```bash
# Navigate to the essen-demo directory
cd /path/to/VirtPLC/essen-demo

# Start PLC services
docker-compose -f docker-compose.plc.yml up -d

# Verify services are running
docker-compose -f docker-compose.plc.yml ps
```

**Access Points:**
- Node-RED: http://localhost:1880
- Ignition Edge: http://localhost:8088
- RabbitMQ Management: http://localhost:15672 (user: virtplc, pass: virtplc123)

### Step 2: Historian Server Setup
On the Historian server:

```bash
# Navigate to the essen-demo directory
cd /path/to/VirtPLC/essen-demo

# Start data services
docker-compose -f docker-compose.data.yml up -d

# Verify services are running
docker-compose -f docker-compose.data.yml ps
```

**Access Points:**
- PostgreSQL: localhost:5432
- TimescaleDB: localhost:5433

### Step 3: Windows Machine Setup
On the Windows machine (with Unreal Engine):

```bash
# Navigate to the essen-demo directory
cd /path/to/VirtPLC/essen-demo

# Set the PLC IP (replace with actual PLC machine IP)
export PLC_IP=<PLC_MACHINE_IP>

# Start simulator services
docker-compose -f docker-compose.simulator.yml up -d

# Verify services are running
docker-compose -f docker-compose.simulator.yml ps
```

**Access Points:**
- Simulator API: http://localhost:5000
- Simulator Monitor: http://localhost:5002

### Step 4: Main AI PC Setup
On the Main AI PC (Linux):

```bash
# Navigate to the essen-demo directory
cd /path/to/VirtPLC/essen-demo

# Create external networks (run once)
docker network create --driver bridge --subnet=172.21.0.0/16 virtplc_data_network
docker network create --driver bridge --subnet=172.20.0.0/16 virtplc_plc_network

# Set environment variables with actual IPs
export HISTORIAN_IP=<HISTORIAN_SERVER_IP>
export PLC_IP=<PLC_MACHINE_IP>
export WINDOWS_IP=<WINDOWS_MACHINE_IP>

# Start main application services
docker-compose -f docker-compose.main.yml up -d

# Verify services are running
docker-compose -f docker-compose.main.yml ps
```

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:18080
- Collector: http://localhost:8082
- MCP: http://localhost:3001
- AI Service: http://localhost:8001

## Inter-Computer Communication

The services communicate across computers using IP addresses. Set the following environment variables before running docker-compose:

- `HISTORIAN_IP`: IP of the Historian server
- `PLC_IP`: IP of the PLC machine
- `WINDOWS_IP`: IP of the Windows machine

These are used in the docker-compose files for cross-machine connections.

## Data Flow

1. **Unreal Engine** → MQTT → **Node-RED** (PLC)
2. **Node-RED** → MQTT → **Ignition Edge** (PLC)
3. **Python Simulator** → MQTT → **Node-RED** (PLC)
4. **Node-RED** → MQTT → **Collector** (Main AI PC)
5. **Collector** → Database → **TimescaleDB/PostgreSQL** (Historian Server)
6. **Backend** → Database → **TimescaleDB/PostgreSQL** (Historian Server)
7. **Frontend** → API → **Backend** (Main AI PC)

## Monitoring and Troubleshooting

### Check Service Health
```bash
# On each computer, check service status
docker-compose -f docker-compose.<type>.yml ps
docker-compose -f docker-compose.<type>.yml logs <service_name>
```

### Network Connectivity
```bash
# Test connectivity between computers
ping <other_computer_ip>

# Test service ports
telnet <service_ip> <port>
```

### Common Issues

1. **Network connectivity**: Ensure firewalls allow the required ports
2. **DNS resolution**: Use IP addresses instead of hostnames for cross-computer communication
3. **Time synchronization**: Ensure all computers have synchronized clocks for timestamp consistency

## Scaling and High Availability

For production deployment:
- Use Docker Swarm or Kubernetes for orchestration
- Implement load balancers for high availability
- Add monitoring with Prometheus/Grafana
- Configure backups for databases
- Use SSL/TLS for secure communication

## Development vs Production

These configurations are optimized for the Essen demo. For development:
- Use the main `docker-compose.yml` in the project root
- All services run on a single machine
- Simplified networking

For production:
- Use these multi-computer configurations
- Implement proper security measures
- Add monitoring and logging
- Configure backups and disaster recovery