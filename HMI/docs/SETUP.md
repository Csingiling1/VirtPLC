# VirtPLC HMI Setup Guide

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Initial Configuration](#initial-configuration)
4. [Testing](#testing)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4 GB
- Disk: 20 GB free space
- Network: 100 Mbps

**Recommended (Production):**
- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 50+ GB SSD
- Network: 1 Gbps

### Software Requirements

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Operating System**:
  - Linux (Ubuntu 20.04+, RHEL 8+, CentOS 8+)
  - Windows 10/11 with WSL2
  - macOS 11+

### Network Ports

Ensure the following ports are available:

| Port | Service | Purpose |
|------|---------|---------|
| 8088 | Ignition Gateway (HTTP) | Web interface |
| 8043 | Ignition Gateway (HTTPS) | Secure web interface |
| 8060 | Gateway Network | Inter-gateway communication |
| 4840 | OPC-UA Server | Equipment data |
| 8011 | TimeBase | Historical database |
| 5432 | PostgreSQL | Relational database |
| 6379 | Redis | Cache |
| 3000 | Grafana | Monitoring dashboards |
| 9091 | Prometheus | Metrics collection |

## Installation Steps

### Step 1: Clone Repository

```bash
git clone https://github.com/Dedzsinator/VirtPLC.git
cd VirtPLC/HMI
```

### Step 2: Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit with your preferred editor
nano .env

# Configure these critical variables:
# - GATEWAY_PASSWORD (change from default!)
# - POSTGRES_PASSWORD
# - GRAFANA_PASSWORD
```

### Step 3: Verify Docker Installation

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Verify Docker is running
docker ps
```

### Step 4: Start Services

```bash
# Pull images (may take several minutes on first run)
docker-compose pull

# Start all services
docker-compose up -d

# Verify all services are running
docker-compose ps

# Expected output: All services should show "Up" status
```

### Step 5: Wait for Initialization

```bash
# Monitor gateway startup (press Ctrl+C to exit)
docker-compose logs -f ignition-gateway

# Wait for message: "Gateway started successfully"
# This typically takes 2-3 minutes on first start
```

### Step 6: Verify Installation

```bash
# Check health of all services
docker-compose ps

# Test gateway HTTP endpoint
curl http://localhost:8088/StatusPing

# Expected: HTTP 200 OK
```

## Initial Configuration

### Gateway Web Interface

1. **Access Gateway**
   - Navigate to: `http://localhost:8088`
   - Login with: `admin` / `password` (or your configured password)

2. **First Login Wizard**
   - Change admin password (highly recommended!)
   - Configure time zone
   - Set up email for notifications

3. **License Activation**
   - Ignition Edge includes a 2-hour runtime license (resets every 24 hours)
   - For production, purchase and activate a full license
   - Navigate to: Config → Licensing

### Configure OPC-UA Connection

1. **Open Connections**
   - Navigate to: Config → OPC UA → Connections
   - Find "Backend-OPC-UA"

2. **Verify Connection**
   - Click "Edit"
   - Endpoint should be: `opc.tcp://backend:4840`
   - Click "Test" to verify connectivity

3. **Connection Settings**
   - Security Policy: None (change for production!)
   - Authentication: Anonymous
   - Click "Save"

### Configure Tag Provider

1. **Access Tag Browser**
   - Navigate to: Config → Tags → Tag Browser

2. **Import Tag Definitions**
   - Click "More Tools" → "Import Tags"
   - Select: `/config/tag-definitions.json` from mounted volume
   - Click "Import"

3. **Verify Tags**
   - Expand "default" provider
   - Verify folders: Motor1, Motor2, Conveyor1, System
   - Check tag quality (should be "Good")

### Configure Historical Data

1. **Tag History Configuration**
   - Navigate to: Config → Tag History → Providers
   - Verify "default" provider exists

2. **Storage Provider**
   - Database: timebase
   - Verify connection is active
   - Click "Test Connection"

3. **Enable History**
   - Navigate to Tag Browser
   - Right-click tags with history enabled
   - Verify "History Enabled" is checked

### Configure Alarms

1. **Alarm Configuration**
   - Navigate to: Config → Alarming
   - Verify alarm journal is configured

2. **Notification Pipelines**
   - Navigate to: Config → Alarming → Notification
   - Review existing pipelines:
     - Critical-Alerts (for urgent issues)
     - High-Alerts (for important notifications)

3. **Test Alarm**
   - Navigate to Perspective → Alarms view
   - Trigger a test alarm (overspeed Motor1)
   - Verify alarm appears and can be acknowledged

### Open Perspective Session

1. **Launch Project**
   - Navigate to: Home → Perspective → Projects
   - Click "Launch" on VirtPLC-HMI

2. **Alternative Direct Access**
   - URL: `http://localhost:8088/data/perspective/client/VirtPLC-HMI`

3. **Test Navigation**
   - Navigate through all views:
     - Overview
     - Motor Control
     - Conveyor Control
     - Alarms
     - Trends

## Testing

### Manual Testing

#### Test Motor Control

1. **Start Motor 1**
   - Navigate to Motor Control view
   - Click "START" button for Motor 1
   - Observe status changes to "RUNNING"
   - Watch speed gauge ramp up

2. **Adjust Speed**
   - Change "Target Speed" value
   - Click motor to update
   - Observe speed adjusts to new target

3. **Stop Motor**
   - Click "STOP" button
   - Verify status changes to "STOPPED"
   - Watch speed ramp down to zero

#### Test Conveyor Control

1. **Prerequisites**
   - Ensure Motor 1 is running (conveyor dependency)

2. **Start Conveyor**
   - Navigate to Conveyor Control view
   - Click "START CONVEYOR"
   - Verify conveyor shows "RUNNING"
   - Watch item count increment

3. **Stop Conveyor**
   - Click "STOP CONVEYOR"
   - Verify conveyor stops
   - Item count should persist

#### Test Emergency Stop

1. **Trigger E-Stop**
   - Navigate to Conveyor Control view
   - Click "EMERGENCY" button
   - **Verify all equipment stops immediately**

2. **Reset System**
   - Navigate to Motor Control
   - Click "SYSTEM RESET" (if visible)
   - Or navigate to Overview and reset

### Automated Testing

```bash
# Run unit tests
cd HMI
pytest tests/test_tag_operations.py -v

# Run integration tests
pytest tests/test_integration.py -v

# Run E2E tests (requires HMI to be running)
pytest tests/test_e2e.py -v -m "e2e"

# Run all tests with coverage
pytest tests/ -v --cov --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Verify Historical Data

1. **Check TimeBase**
   - Wait 5-10 minutes for data collection
   - Navigate to Trends view
   - Verify charts show historical data
   - Adjust time range (1 hour, 24 hours, etc.)

2. **Query TimeBase Directly**
   ```bash
   # Access TimeBase CLI
   docker-compose exec timebase timebase-cli
   
   # List streams
   list streams
   
   # Query data
   select * from motor_telemetry limit 10
   ```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Change all default passwords
- [ ] Configure SSL/TLS certificates
- [ ] Set up backup strategy
- [ ] Configure monitoring and alerting
- [ ] Review and harden security settings
- [ ] Test disaster recovery procedures
- [ ] Document custom configurations
- [ ] Train operators on HMI usage

### SSL/TLS Configuration

1. **Generate Certificates**
   ```bash
   mkdir -p certs
   
   # Self-signed (testing only)
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout certs/server.key \
     -out certs/server.crt
   
   # Production: Use certificates from CA
   ```

2. **Update Configuration**
   ```bash
   # Edit .env
   SSL_ENABLED=true
   SSL_CERT_PATH=/certs/server.crt
   SSL_KEY_PATH=/certs/server.key
   ```

3. **Update Gateway**
   - Navigate to Config → Web Server
   - Enable HTTPS
   - Upload certificate and key
   - Force HTTPS redirect

### Backup Configuration

1. **Automated Backup**
   ```bash
   # Configure in gateway.xml
   <backup>
     <enabled>true</enabled>
     <schedule>
       <frequency>daily</frequency>
       <time>02:00</time>
     </schedule>
     <retention>7</retention>
   </backup>
   ```

2. **Manual Backup**
   ```bash
   # Backup gateway
   docker-compose exec ignition-gateway \
     /usr/local/bin/ignition/gwcmd.sh --backup /backup/manual.zip
   
   # Backup databases
   docker-compose exec postgres pg_dump virtplc > backup_postgres.sql
   docker-compose exec timebase timebase backup > backup_timebase.tar.gz
   ```

### Monitoring Setup

1. **Grafana Dashboards**
   - Access: `http://localhost:3000`
   - Login: admin / admin (change!)
   - Import dashboards from `/monitoring/grafana/dashboards/`

2. **Prometheus Alerts**
   - Edit: `/monitoring/prometheus/alerts.yml`
   - Configure alert rules for:
     - High CPU/memory usage
     - Service downtime
     - Database connection failures
     - Excessive alarm rates

### Load Balancer Configuration

For production high availability:

```nginx
# nginx.conf example
upstream ignition_backend {
    server ignition-1.local:8088;
    server ignition-2.local:8088;
}

server {
    listen 80;
    server_name hmi.company.com;
    
    location / {
        proxy_pass http://ignition_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Common Issues

#### Issue: Gateway Won't Start

**Symptoms:**
- Container exits immediately
- "Port already in use" error

**Solutions:**
```bash
# Check if port is in use
sudo netstat -tlnp | grep 8088

# Stop conflicting service or change port in .env
GATEWAY_HTTP_PORT=8089

# Check logs
docker-compose logs ignition-gateway

# Restart services
docker-compose restart ignition-gateway
```

#### Issue: Tags Show "Bad" Quality

**Symptoms:**
- All tags show "Bad" quality
- No real-time data updates

**Solutions:**
```bash
# Verify OPC-UA server is running
docker-compose ps backend-opcua

# Restart OPC-UA connection in gateway
# Config → OPC UA → Connections → Backend-OPC-UA → Restart

# Check firewall
sudo iptables -L | grep 4840

# View detailed logs
docker-compose logs backend-opcua
```

#### Issue: Historical Data Not Logging

**Symptoms:**
- Trends show no data
- TimeBase connection failures

**Solutions:**
```bash
# Check TimeBase status
docker-compose ps timebase
docker-compose logs timebase

# Verify tag history configuration
# Config → Tag History → Verify provider is enabled

# Test TimeBase connection
docker-compose exec ignition-gateway \
  curl http://timebase:8011/health

# Restart TimeBase
docker-compose restart timebase
```

#### Issue: High Memory Usage

**Symptoms:**
- System slowdown
- Out of memory errors

**Solutions:**
```bash
# Check current usage
docker stats

# Increase memory limits in docker-compose.yml
# For ignition-gateway:
deploy:
  resources:
    limits:
      memory: 4G

# Restart with new limits
docker-compose up -d
```

### Getting Help

1. **Check Logs**
   ```bash
   # All services
   docker-compose logs --tail=100
   
   # Specific service
   docker-compose logs -f ignition-gateway
   ```

2. **Service Status**
   ```bash
   # Check all services
   docker-compose ps
   
   # Check specific service health
   docker inspect virtplc-hmi-gateway
   ```

3. **System Resources**
   ```bash
   # Monitor resources
   docker stats
   
   # Disk usage
   docker system df
   ```

4. **Contact Support**
   - GitHub Issues: https://github.com/Dedzsinator/VirtPLC/issues
   - Documentation: `/docs` directory
   - Ignition Forum: https://forum.inductiveautomation.com

## Next Steps

After successful installation:

1. **Customize Views**
   - Modify layouts to match your facility
   - Add custom components
   - Configure user preferences

2. **Configure Alarm Notifications**
   - Set up email notifications
   - Configure SMS alerts
   - Integrate with ticketing systems

3. **Create Custom Reports**
   - Design production reports
   - Set up scheduled exports
   - Configure dashboard PDFs

4. **Train Operators**
   - Conduct training sessions
   - Create user documentation
   - Set up role-based access

5. **Plan Maintenance**
   - Schedule regular backups
   - Plan system updates
   - Review security patches

---

**Congratulations!** Your VirtPLC HMI system is now operational. 🎉
