# VirtPLC Deployment Guide

## Quick Start Options

### Option 1: All-in-One (Development/Testing)

Best for: Local testing, development, demonstrations

```bash
# Use the original docker-compose (all services on one machine)
cd HMI
cp .env.example .env
docker-compose up -d

# Access HMI
open http://localhost:8088/data/perspective/client/VirtPLC-HMI

# Access Simulator Dashboard
open http://localhost:8080
```

### Option 2: Separate Backend + Edge (Production)

Best for: Production deployment, multiple edge devices, scalability

#### Step 1: Deploy Backend Server

```bash
# On backend server (e.g., 192.168.1.100)
cd HMI
cp .env.backend .env

# Edit .env and change passwords
nano .env

# Start backend services
docker-compose -f docker-compose.backend.yml up -d

# Verify all services are running
docker-compose -f docker-compose.backend.yml ps

# Check logs
docker-compose -f docker-compose.backend.yml logs -f
```

**Backend Services Started:**
- ✅ TimeBase (port 8011)
- ✅ PostgreSQL (port 5432)
- ✅ Redis (port 6379)
- ✅ Grafana (port 3000)
- ✅ Prometheus (port 9090)

#### Step 2: Deploy Edge Device(s)

```bash
# On edge device (tablet, industrial PC, etc.)
cd HMI
cp .env.edge .env

# CRITICAL: Edit .env and set BACKEND_SERVER_IP
nano .env
# Change: BACKEND_SERVER_IP=192.168.1.100

# Start edge services
docker-compose -f docker-compose.edge.yml up -d

# Verify services
docker-compose -f docker-compose.edge.yml ps

# Check logs
docker-compose -f docker-compose.edge.yml logs -f ignition-edge
```

**Edge Services Started:**
- ✅ Ignition Edge Gateway (port 8088)
- ✅ PLC Simulator (port 4840, 8080)

#### Step 3: Access HMI from Any Device

From any device on the same network:

**On PC/Laptop:**
```
http://<edge-device-ip>:8088/data/perspective/client/VirtPLC-HMI
```

**On Tablet:**
- Open browser (Chrome/Safari/Firefox)
- Navigate to: `http://<edge-device-ip>:8088/data/perspective/client/VirtPLC-HMI`
- Add to home screen for app-like experience

**On Phone:**
- Open mobile browser
- Navigate to: `http://<edge-device-ip>:8088/data/perspective/client/VirtPLC-HMI`
- Portrait mode works, landscape recommended

### Option 3: Testing Without Ignition (Simulator Only)

Best for: Testing the PLC simulator before setting up Ignition

```bash
# Just run the simulator
cd HMI/simulator
pip install -r requirements.txt
python simulator.py

# In another terminal, access simulator dashboard
python web_api.py

# Open dashboard
open http://localhost:8080
```

## Network Configuration Examples

### Example 1: Single Location

```
Router: 192.168.1.1
Backend Server: 192.168.1.100
Edge Device 1: 192.168.1.101
Edge Device 2: 192.168.1.102

Access from phone: http://192.168.1.101:8088/data/perspective/client/VirtPLC-HMI
```

### Example 2: Cloud Backend + Local Edge

```
Cloud Backend: backend.company.com (public IP: 203.0.113.45)
Local Edge: 192.168.1.50

# On edge device .env:
BACKEND_SERVER_IP=backend.company.com

# Or use IP:
BACKEND_SERVER_IP=203.0.113.45

# Configure cloud firewall to allow:
# - Port 8011 (TimeBase) from edge device IP
# - Port 5432 (PostgreSQL) from edge device IP
# - Port 6379 (Redis) from edge device IP
```

### Example 3: Multiple Factories

```
HQ Backend: 10.0.0.100

Factory 1 Edge: 10.1.0.50
Factory 2 Edge: 10.2.0.50
Factory 3 Edge: 10.3.0.50

# All edge devices set:
BACKEND_SERVER_IP=10.0.0.100

# VPN tunnels connect factories to HQ
```

## Hardware Recommendations

### Backend Server Options

#### Cloud (Recommended for Multi-Site)
**AWS EC2 t3.large**
- 2 vCPU, 8 GB RAM
- 100 GB EBS Storage
- Cost: ~$60-80/month

**Azure Standard B2ms**
- 2 vCPU, 8 GB RAM
- Cost: ~$70/month

**DigitalOcean Droplet**
- 4 vCPU, 8 GB RAM
- Cost: ~$48/month

#### On-Premise Server
**Dell PowerEdge R340**
- Intel Xeon E-2234, 16 GB RAM
- Cost: ~$1,500

**HPE ProLiant ML110**
- Intel Xeon, 16 GB RAM
- Cost: ~$1,200

**Mini PC (Budget)**
- Intel NUC or similar
- i5, 16 GB RAM
- Cost: ~$500-700

### Edge Device Options

#### For Tablets
**Panasonic Toughbook**
- Rugged, industrial rated
- 4-8 GB RAM
- Cost: $2,000-3,000
- Best for: Harsh environments

**Samsung Galaxy Tab Active Pro**
- IP68 rated, 4 GB RAM
- Cost: $600-800
- Best for: Mobile operators

#### For Industrial PC
**Advantech ARK-1123H**
- Fanless, Intel Core i5
- 8 GB RAM
- Cost: $800-1,200
- Best for: Fixed installations

**Siemens SIMATIC IPC427E**
- Industrial PC, 4-8 GB RAM
- Cost: $1,500-2,500
- Best for: Mission-critical

#### For Raspberry Pi (Budget)
**Raspberry Pi 5 (8GB)**
- Cost: $80
- Best for: Light load, testing
- Note: ARM architecture, may need image adjustments

#### For Standard Laptop/PC
**Any Modern Laptop**
- i5/Ryzen 5, 8 GB RAM
- Cost: $500-1,000
- Best for: Testing, temporary

## Testing the Simulator

### Test Scenario 1: Motor Start/Stop

1. **Access Simulator Dashboard**
   ```
   http://<edge-ip>:8080
   ```

2. **Access HMI**
   ```
   http://<edge-ip>:8088/data/perspective/client/VirtPLC-HMI
   ```

3. **Start Motor 1**
   - Click "START" on Motor Control view
   - Observe on simulator dashboard:
     - State changes: STOPPED → STARTING → RUNNING
     - Speed ramps up to target
     - Temperature increases
     - Current and power increase

4. **Stop Motor**
   - Click "STOP"
   - Observe speed ramp down
   - Temperature decreases

### Test Scenario 2: Fault Simulation

1. **Trigger Overspeed**
   - Set target speed to 2500 RPM (exceeds 2200 limit)
   - Motor will fault after reaching overspeed
   - Observe fault code 101 (Overspeed)

2. **Clear Fault**
   - Click "RESET" button
   - Set reasonable target speed (< 2200)
   - Click "START" again

### Test Scenario 3: Emergency Stop

1. **Trigger E-Stop**
   - On Conveyor Control view, click "EMERGENCY"
   - **All equipment stops immediately**
   - Simulator shows EMERGENCY_STOP state

2. **Reset System**
   - Navigate to Motor Control
   - Click "SYSTEM RESET" (if visible)
   - Equipment returns to STOPPED state

### Test Scenario 4: Conveyor with Interlock

1. **Try Starting Conveyor (Motor Stopped)**
   - Conveyor will NOT start
   - Check simulator logs: "motor interlock not satisfied"

2. **Start Motor 1 First**
   - Motor must be running

3. **Start Conveyor**
   - Now conveyor starts successfully
   - Item count begins incrementing

## Monitoring

### Grafana Dashboards

Access: `http://<backend-ip>:3000`

**Default Login:**
- Username: admin
- Password: (from .env GRAFANA_PASSWORD)

**Available Dashboards:**
- System Overview
- Motor Performance
- Historical Trends
- Alarm Statistics

### Prometheus Metrics

Access: `http://<backend-ip>:9090`

**Query Examples:**
```
# Motor speed
motor_speed{motor="Motor1"}

# Temperature
motor_temperature{motor="Motor1"}

# Conveyor items
conveyor_items{conveyor="Conveyor1"}
```

### Simulator Dashboard

Access: `http://<edge-ip>:8080`

**Features:**
- Real-time state visualization
- Live metrics update
- Color-coded status
- Auto-refresh every 2 seconds

## Troubleshooting

### Edge Cannot Connect to Backend

**Problem:** Edge device can't reach backend services

**Solutions:**
1. **Check network connectivity**
   ```bash
   ping <backend-ip>
   ```

2. **Test specific ports**
   ```bash
   nc -zv <backend-ip> 8011  # TimeBase
   nc -zv <backend-ip> 5432  # PostgreSQL
   nc -zv <backend-ip> 6379  # Redis
   ```

3. **Check backend firewall**
   ```bash
   # On backend server
   sudo ufw allow 8011
   sudo ufw allow 5432
   sudo ufw allow 6379
   ```

4. **Verify .env configuration**
   ```bash
   cat .env | grep BACKEND_SERVER_IP
   # Should show correct backend IP
   ```

### OPC-UA Connection Failed

**Problem:** Ignition cannot connect to PLC simulator

**Solutions:**
1. **Check simulator is running**
   ```bash
   docker-compose -f docker-compose.edge.yml logs plc-simulator
   ```

2. **Test OPC-UA endpoint**
   ```bash
   # Install OPC-UA client
   pip install opcua
   
   # Test connection
   python -c "from opcua import Client; c=Client('opc.tcp://localhost:4840/virtplc/'); c.connect(); print('OK'); c.disconnect()"
   ```

3. **Check Ignition OPC-UA configuration**
   - Navigate to: Config → OPC UA → Connections
   - Endpoint should be: `opc.tcp://plc-simulator:4840/virtplc/`
   - Click "Edit" → "Test Connection"

### HMI Not Loading on Mobile

**Problem:** Cannot access HMI from phone/tablet

**Solutions:**
1. **Verify same network**
   - Edge device and mobile must be on same WiFi

2. **Check edge device IP**
   ```bash
   # On edge device
   hostname -I
   ```

3. **Test from mobile browser**
   ```
   http://<edge-ip>:8088/StatusPing
   # Should return "OK"
   ```

4. **Disable browser cache**
   - Force refresh on mobile
   - Clear browser cache

5. **Try HTTPS**
   - Some corporate networks block HTTP
   - Configure SSL in Ignition Gateway

## Performance Tuning

### Backend Server

**High Load (many edge devices):**
```yaml
# In docker-compose.backend.yml, increase resources:
services:
  postgres:
    deploy:
      resources:
        limits:
          memory: 2G  # Increase from 1G
  
  timebase:
    environment:
      - TIMEBASE_MEMORY=4096M  # Increase from 2048M
```

### Edge Device

**Low Memory Device (Raspberry Pi):**
```yaml
# In docker-compose.edge.yml:
services:
  ignition-edge:
    environment:
      - JAVA_OPTS=-Xmx256m -Xms128m  # Reduce from 512m
```

**Reduce Simulation Speed:**
```yaml
# In .env:
SIMULATION_SPEED=0.5  # Run at half speed
```

## Security Best Practices

### Production Checklist

- [ ] Change all default passwords
- [ ] Enable SSL/TLS on Ignition Gateway
- [ ] Configure PostgreSQL authentication (not trust mode)
- [ ] Use VPN for remote access
- [ ] Firewall rules (whitelist only necessary IPs)
- [ ] Regular backups (automated daily)
- [ ] Update Docker images regularly
- [ ] Enable Ignition audit logging
- [ ] Configure role-based access control (RBAC)
- [ ] Monitor system logs

### SSL Configuration

```bash
# Generate self-signed certificate (testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout server.key -out server.crt

# In Ignition Gateway:
# Config → Web Server → HTTPS
# Upload certificate and key
# Enable "Force HTTPS"
```

## Scaling Up

### Adding More Edge Devices

1. **Clone edge configuration**
   ```bash
   # On new edge device
   git clone <repo>
   cd HMI
   cp .env.edge .env
   ```

2. **Configure backend IP**
   ```bash
   nano .env
   # Set BACKEND_SERVER_IP
   ```

3. **Start services**
   ```bash
   docker-compose -f docker-compose.edge.yml up -d
   ```

4. **Each device is independent**
   - Own Ignition Gateway
   - Own PLC simulator
   - All connect to same backend

### Backend High Availability

**PostgreSQL Replication:**
```yaml
# Add replica in docker-compose.backend.yml
services:
  postgres-replica:
    image: postgres:15-alpine
    environment:
      - POSTGRESQL_REPLICATION_MODE=slave
      - POSTGRESQL_MASTER_HOST=postgres
```

**TimeBase Clustering:**
- Requires TimeBase Enterprise license
- Contact Deltix for configuration

## Next Steps

1. **Test locally first** (Option 1: All-in-One)
2. **Deploy backend** to server/cloud
3. **Deploy edge** to device
4. **Configure network** (firewall, VPN)
5. **Test connectivity** between edge and backend
6. **Access HMI** from mobile/tablet
7. **Monitor** via Grafana
8. **Train operators**
9. **Go live!**

## Support

- **Documentation:** `/docs` directory
- **GitHub Issues:** https://github.com/Dedzsinator/VirtPLC/issues
- **Simulator API Docs:** `http://<edge-ip>:8080/docs`
- **Ignition Forums:** https://forum.inductiveautomation.com

---

**Ready to deploy? Start with Option 1 to test everything locally first!** 🚀
